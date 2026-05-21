import json
import re
import tempfile
import os
from pathlib import Path

import duckdb
import pandas as pd
import sqlglot

from api.models import MEASURES_COLUMNS

MODELS_DIR = Path(__file__).resolve().parent.parent / "core" / "models"

# Parquet table name → schema in the in-memory DuckDB
_PRECOMPUTED_SCHEMA_MAP = {
    "global_parameters": "core_layer0_base",
    "value_stream_groups": "core_layer0_base",
    "program_value_streams": "core_layer0_base",
    "avoided_costs_ts": "core_layer0_base",
    "load_shapes_ts": "core_layer0_base",
    "cost_treatment_factors": "core_layer0_base",
    "avoided_cost_load_shape_combos": "core_layer2_precompute",
}


def _sql_body(path: Path) -> str:
    """Strip the SQLMesh MODEL(...) header, remove the openbca catalog prefix, and transpile
    type syntax (MAP<K,V>, ARRAY<T>) to DuckDB-native equivalents via sqlglot.

    Also applies a targeted fix for DuckDB's ambiguous ORDER BY resolution when wildcard
    EXCLUDE is in play: replaces bare 'id' in ORDER BY with the qualified 'tv.id'.
    """
    text = path.read_text()
    text = re.sub(r"\bopenbca\.", "", text)
    raw = text[text.index(");") + 2:].strip()
    sql = sqlglot.transpile(raw, read="duckdb", write="duckdb")[0]
    # DuckDB cannot resolve bare 'id' in ORDER BY when multiple joined tables all have an
    # 'id' column, even after wildcard EXCLUDE removes them. Use qualified name instead.
    sql = re.sub(r"\bORDER BY(\s+type\s*,\s*)id\b", r"ORDER BY\1tv.id", sql)
    return sql


def _create_schemas(con: duckdb.DuckDBPyConnection) -> None:
    for schema in [
        "openbca_input",
        "core_layer0_base",
        "core_layer1_mappings",
        "core_layer2_precompute",
        "core_layer3_finalization",
    ]:
        con.execute(f"CREATE SCHEMA {schema}")


def _register_precomputed(
    con: duckdb.DuckDBPyConnection,
    precomputed: dict[str, str],
) -> None:
    """Register pre-computed parquet files in the in-memory DuckDB.

    Large tables are registered as VIEWs reading parquet on demand (so DuckDB can stream
    them during JOINs without fully materializing them). Small config tables are copied
    into DuckDB TABLEs for repeated lookups.
    """
    # Large: stream from parquet during query execution
    _large = {"avoided_cost_load_shape_combos", "avoided_costs_ts", "load_shapes_ts"}

    for name, schema in _PRECOMPUTED_SCHEMA_MAP.items():
        parquet_path = precomputed[name]
        if name in _large:
            con.execute(
                f"CREATE VIEW {schema}.{name} AS SELECT * FROM '{parquet_path}'"
            )
        else:
            con.execute(
                f"CREATE TABLE {schema}.{name} AS SELECT * FROM '{parquet_path}'"
            )

    # layer0_base/measures.sql reads openbca_input.global_parameters directly
    con.execute(
        "CREATE VIEW openbca_input.global_parameters AS "
        "SELECT * FROM core_layer0_base.global_parameters"
    )


def _load_measures(con: duckdb.DuckDBPyConnection, measures: list[dict]) -> None:
    df = pd.DataFrame(measures)
    for col in MEASURES_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[MEASURES_COLUMNS]
    con.register("_tmp_measures", df)
    con.execute("CREATE TABLE openbca_input.measures AS SELECT * FROM _tmp_measures")


# Dependencies between layer3 models (which tables must exist before building each)
_LAYER3_DEPS: dict[str, set[str]] = {
    "final_savings_calculations_ts": set(),
    "final_value_calculations_ts": set(),
    "jst_ratio": {"final_value_calculations_ts"},
    "results_summary_by_id": {"final_value_calculations_ts"},
}

_LAYER3_BUILD_ORDER = [
    "final_savings_calculations_ts",
    "final_value_calculations_ts",
    "jst_ratio",
    "results_summary_by_id",
]


def _resolve_layer3(requested: set[str]) -> list[str]:
    needed: set[str] = set()
    for m in requested:
        needed.add(m)
        needed.update(_LAYER3_DEPS[m])
    return [m for m in _LAYER3_BUILD_ORDER if m in needed]


def _create_views(con: duckdb.DuckDBPyConnection, layer3_models: list[str]) -> None:
    # Layer 0: measures view
    con.execute(
        "CREATE VIEW core_layer0_base.measures AS "
        + _sql_body(MODELS_DIR / "layer0_base" / "measures.sql")
    )

    # Layer 1 mappings
    for name in [
        "commodity_load_shape_by_id",
        "avoided_cost_subsets_by_id",
        "cost_components_by_id",
    ]:
        con.execute(
            f"CREATE VIEW core_layer1_mappings.{name} AS "
            + _sql_body(MODELS_DIR / "layer1_mappings" / f"{name}.sql")
        )

    # Layer 2: savings_factors (avoided_cost_load_shape_combos already a view)
    con.execute(
        "CREATE VIEW core_layer2_precompute.savings_factors AS "
        + _sql_body(MODELS_DIR / "layer2_precompute" / "savings_factors.sql")
    )

    # Layer 3: materialize only requested models (and their dependencies).
    # results_summary_by_id uses dynamic PIVOT which DuckDB forbids in VIEWs, so all
    # layer3 models are created as TABLEs.
    for name in layer3_models:
        con.execute(
            f"CREATE TABLE core_layer3_finalization.{name} AS "
            + _sql_body(MODELS_DIR / "layer3_finalization" / f"{name}.sql")
        )


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))


def _fetch_results(con: duckdb.DuckDBPyConnection, layer3_models: set[str]) -> dict:
    result: dict = {}
    if "jst_ratio" in layer3_models:
        rows = _df_to_records(con.execute("SELECT * FROM core_layer3_finalization.jst_ratio").df())
        result["jst_ratio"] = rows[0] if rows else {}
    if "results_summary_by_id" in layer3_models:
        result["results_summary"] = _df_to_records(
            con.execute("SELECT * FROM core_layer3_finalization.results_summary_by_id").df()
        )
    if "final_value_calculations_ts" in layer3_models:
        result["final_value_calculations"] = _df_to_records(
            con.execute("SELECT * FROM core_layer3_finalization.final_value_calculations_ts").df()
        )
    if "final_savings_calculations_ts" in layer3_models:
        result["net_energy_savings"] = _df_to_records(
            con.execute("SELECT * FROM core_layer3_finalization.final_savings_calculations_ts").df()
        )
    return result


def run(
    measures: list[dict],
    precomputed: dict[str, str],
    outputs: set[str] | None = None,
) -> dict:
    """Run layer3 calculations for the given measures.

    Args:
        measures: list of measure dicts (keys matching MEASURES_COLUMNS)
        precomputed: dict mapping table name → parquet file path (from precompute.load)
        outputs: which layer3 models to build; defaults to all four
    """
    if outputs is None:
        outputs = set(_LAYER3_DEPS.keys())
    layer3_models = _resolve_layer3(outputs)

    # Use a temp file-backed DuckDB so DuckDB can spill to disk for large computations.
    # Generate a unique path but don't create the file — DuckDB must create it fresh.
    tmp_path = tempfile.mktemp(suffix=".db")  # noqa: S306 (temp path only, not created)
    try:
        con = duckdb.connect(tmp_path)
        try:
            _create_schemas(con)
            _register_precomputed(con, precomputed)
            _load_measures(con, measures)
            _create_views(con, layer3_models)
            return _fetch_results(con, outputs)
        finally:
            con.close()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
