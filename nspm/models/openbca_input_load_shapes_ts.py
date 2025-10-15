from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd
import os

ID_COLUMNS = [
    "commodity", "year","quarter", "month", "day", "hour_of_year"
]

@model(
    name="nspm.openbca_input_load_shapes_ts",
    kind="FULL",
    grain=ID_COLUMNS,
    columns={
        "commodity": "string",
        "year": "int",
        "day": "int",
        "hour_of_year": "int",
        "load_shape": "string",
        "value": "float",
    },
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_timeseries_from_excel(
        input_file="OpenBCA Code PROGRAM INPUT.xlsx",
        skip_sheets={"Front Page", "Program Inputs", "Measure Inputs", "Define Load Shape Names"},
        skiprows=1,
    )


BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, "..", "Input")  # adjust if needed


def load_timeseries_from_excel(
    input_file: str,
    skip_sheets: set,
    skiprows: int = 1,
) -> DataFrame:
    """
    Load and consolidate timeseries data from an Excel workbook,
    pivoting to long format.
    """
    file_path = os.path.join(DATA_DIR, input_file)
    xls = pd.ExcelFile(file_path)
    all_frames = []

    for sheet in xls.sheet_names:
        if sheet in skip_sheets:
            continue

        df = pd.read_excel(xls, sheet_name=sheet, header=None, skiprows=skiprows)
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            continue

        # --- Handle headers ---
        headers = df.iloc[0].astype(str)
        cleaned_headers = []
        for col in headers:
            col_stripped = str(col).strip()
            if col_stripped.lower() in {"year", "month", "day", "hour of year"}:
                cleaned_headers.append(col_stripped.lower().replace(" ", "_"))
            else:
                cleaned_headers.append(col_stripped)  # keep original
        df.columns = cleaned_headers
        df = df[1:]  # drop header row

        # Add commodity (trim "Loadshape Mapping")
        commodity_name = sheet.replace("Loadshape Mapping", "").strip()
        df["commodity"] = commodity_name

        all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    combined = pd.concat(all_frames, ignore_index=True)

    # --- Ensure required ID columns exist ---
    for col in ["year","quarter" "month", "day", "hour_of_year"]:
        if col not in combined.columns:
            combined[col] = pd.NA

    # --- Pivot to long format ---
    id_cols = ["commodity", "year", "day", "hour_of_year"]
    value_vars = [c for c in combined.columns if c not in id_cols]

    long_df = combined.melt(
        id_vars=id_cols,
        value_vars=value_vars,
        var_name="load_shape",
        value_name="value",
    )

    return long_df
