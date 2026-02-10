from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd

from config.paths import get_input_templates_dir


ID_COLUMNS = [
    "commodity", "quarter", "month", "day", "hour_of_year" # Need Quarter?
]

@model(
    name="openbca_input.load_shapes_ts",
    kind="FULL",
    grain=ID_COLUMNS,
    columns={
        "commodity": "string",
        "quarter": "int",
        "month": "int",
        "day_of_year": "int",
        "hour_of_year": "int",
        "load_shape": "string",
        "load_shape_value": "float",
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_load_shapes_from_excel(
        input_file="OpenBCA Program Input.xlsx",
        skip_sheets={"Front Page", "Program Inputs", "Measure Inputs", "Define Load Shape Names", "Updates & Improvements", "Custom Period - LS Support"},
        skiprows=1,
    )

def load_load_shapes_from_excel(
    input_file: str,
    skip_sheets: set,
    skiprows: int = 1,
) -> DataFrame:
    """
    Load and consolidate timeseries data from an Excel workbook,
    pivoting to long format.
    """
    file_path = get_input_templates_dir() / input_file
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
            if col_stripped.lower() in {"month", "day", "hour of year"}:
                cleaned_headers.append(col_stripped.lower().replace(" ", "_"))
            else:
                cleaned_headers.append(col_stripped)  # keep original
        df.columns = cleaned_headers
        df = df[1:]  # drop header row

        # Add commodity (trim "Loadshape Mapping")
        commodity_name = sheet.replace(" Load Shapes", "").strip()
        df["commodity"] = commodity_name

        all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    combined_df = pd.concat(all_frames, ignore_index=True)

    # --- Ensure required ID columns exist ---
    for col in ["quarter", "month", "day", "hour_of_year"]:

        if col not in combined_df.columns:
            combined_df[col] = pd.NA

    # --- Pivot to long format ---
    id_cols = ["commodity", "quarter", "month", "day", "hour_of_year"]
    value_vars = [c for c in combined_df.columns if c not in id_cols]

    long_df = combined_df.melt(
        id_vars=id_cols,
        value_vars=value_vars,
        var_name="load_shape",
        value_name="load_shape_value",
    ).dropna(axis=0, subset=['load_shape_value']).rename({'day': 'day_of_year'}, axis = 1)

    # Adjust hour_of_year from 1 - 8760 to 0 - 8759
    long_df['hour_of_year'] = long_df['hour_of_year'] - 1

    return long_df