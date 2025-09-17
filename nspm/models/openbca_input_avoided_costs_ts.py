from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd
import os

ID_COLUMNS = [
    "commodity","avoided_cost","year", "month", "day", "type_of_day",
    "period", "hour_of_day", "hour_of_year"
]

@model(
    name="nspm.openbca_input_avoided_costs_ts",
    kind="FULL",
    grain=ID_COLUMNS,
    columns={
        "commodity": "string",
        "avoided_cost": "string",
        "avoided_cost_subset": "string",
        "year": "int",
        "month": "int",
        "day": "int",
        "type_of_day": "string",
        "period": "string",
        "hour_of_day": "int",
        "hour_of_year": "int",
        "value": "float",
    },
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_timeseries_from_excel(
        input_file="OpenBCA Code CONFIG File - with Data.xlsm",
        skip_sheets={"Front Page", "Common Data", "Validations", "Configuration Data", "Dictionary"},
        skiprows=2
    )

BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, "..", "Input")  # adjust if needed

def load_timeseries_from_excel(
    input_file: str,
    skip_sheets: set,
    skiprows: int = 2
) -> DataFrame:
    """
    Load and consolidate timeseries data from an Excel workbook,
    enforce schema, and pivot to long format.
    """
    file_path = os.path.join(DATA_DIR, input_file)
    xls = pd.ExcelFile(file_path)
    all_frames = []
    unified_cols = []  # global column order (excluding metadata)

    for sheet in xls.sheet_names:
        if sheet in skip_sheets:
            continue

        # --- Find "Calculation Type" from row 2 ---
        row2 = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=2).iloc[1]  # row index 1 = Excel row 2
        avoided_cost = None
        for cell in row2.dropna().astype(str):
            if "calculation type" in cell.lower():
                # take everything after "Calculation Type:"
                parts = cell.split(":", 1)
                avoided_cost = parts[1].strip() if len(parts) > 1 else cell.strip()
                break

        # --- Load actual data starting at skiprows ---
        df = pd.read_excel(xls, sheet_name=sheet, header=None, skiprows=skiprows)
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            continue

        # Clean headers except those containing "Input"
        raw_headers = df.iloc[0].astype(str)
        cleaned_headers = []
        for col in raw_headers:
            if "input" in col.lower():
                cleaned_headers.append(col.strip())  # keep as-is
            else:
                cleaned_headers.append(str(col).strip().lower().replace(" ", "_").replace("-", "_"))

        df.columns = cleaned_headers
        df = df[1:]

        # Add metadata columns
        df["commodity"] = sheet
        df["avoided_cost"] = avoided_cost

        # Update global order
        for col in df.columns:
            if col not in unified_cols:
                unified_cols.append(col)

        all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    # Align columns across sheets
    aligned_frames = [df.reindex(columns=unified_cols) for df in all_frames]
    combined = pd.concat(aligned_frames, ignore_index=True)

    # ✅ Enforce required column order
    desired_order = [
        "year", "month", "day", "type_of_day",
        "period", "hour_of_day", "hour_of_year"
    ]
    for col in desired_order:
        if col not in combined.columns:
            combined[col] = pd.NA

    # Final order = desired + other inputs + commodity + avoided_cost
    other_cols = [c for c in combined.columns if c not in desired_order and c not in ["commodity", "avoided_cost"]]
    final_order = ["commodity", "avoided_cost"]+desired_order + other_cols 
    combined = combined.reindex(columns=final_order)

    # ✅ Pivot to long format
    df_long = combined.melt(
        id_vars=ID_COLUMNS,
        value_vars=[c for c in combined.columns if c not in ID_COLUMNS],
        var_name="avoided_cost_subset",
        value_name="value"
    )

    # Trim "Input" text if present
    df_long["avoided_cost_subset"] = df_long["avoided_cost_subset"].str.replace("Inputs", "", regex=False)

    return df_long
