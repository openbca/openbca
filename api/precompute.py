import duckdb
from pathlib import Path

# Tables to export from openbca.db to parquet at startup
_EXPORTS = {
    "avoided_costs_ts": "SELECT * FROM core_layer0_base.avoided_costs_ts",
    "load_shapes_ts": "SELECT * FROM core_layer0_base.load_shapes_ts",
    "avoided_cost_load_shape_combos": "SELECT * FROM core_layer2_precompute.avoided_cost_load_shape_combos",
    "global_parameters": "SELECT * FROM core_layer0_base.global_parameters",
    "value_stream_groups": "SELECT * FROM core_layer0_base.value_stream_groups",
    "program_value_streams": "SELECT * FROM core_layer0_base.program_value_streams",
    "cost_treatment_factors": "SELECT * FROM core_layer0_base.cost_treatment_factors",
}


def load(db_path: str) -> dict[str, str]:
    """Export pre-computed tables from openbca.db to parquet files and return their paths.

    Returns a dict mapping table name → absolute parquet file path.
    Called once at server startup; takes ~1 second.
    """
    out_dir = Path(db_path).parent / "api_precomputed"
    out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(db_path, read_only=True)
    try:
        paths: dict[str, str] = {}
        for name, query in _EXPORTS.items():
            out_path = str(out_dir / f"{name}.parquet")
            con.execute(f"COPY ({query}) TO '{out_path}' (FORMAT PARQUET)")
            paths[name] = out_path
    finally:
        con.close()

    return paths
