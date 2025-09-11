from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd
import os

ID_COLUMNS = [
    "year", "month", "day",  "hour_of_year", "source_sheet"
]

@model(
    name="nspm.openbca_input_load_shapes_ts",
    kind="FULL",
    grain=ID_COLUMNS,
    columns={
        "year": "int",
        "month": "int",
        "day": "int",
        "hour_of_year": "int",
        "res_cooling": "float",
        "res_heating": "float", 
        "res_lighting": "float",
        "res_cooking": "float",
        "test1": "float",
        "tes3": "float",
        "test4": "float",
        "tes5": "float",
        "tedst6": "float",
        "test9": "float",
        "test10": "float",
        "test11": "float",
        # dynamic columns from Excel will be treated as string/float
        "source_sheet": "string",
    },
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_timeseries_from_excel(
        input_file="OpenBCA Code PROGRAM INPUT.xlsx",
        skip_sheets={"Front Page", "Program Inputs", "Measure Inputs", "Define Load Shape Names"},
        skiprows=1
    )
BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, "..", "Input")  # adjust if needed

def load_timeseries_from_excel(
    input_file: str,
    skip_sheets: set,
    skiprows: int = 1
) -> DataFrame:
    """
    Load and consolidate timeseries data from an Excel workbook,
    enforcing a consistent schema.
    """
    file_path = os.path.join(DATA_DIR, input_file)
    xls = pd.ExcelFile(file_path)
    all_frames = []
    unified_cols = []  # global column order (excluding source_sheet)

    for sheet in xls.sheet_names:
        if sheet in skip_sheets:
            continue

        df = pd.read_excel(xls, sheet_name=sheet, header=None, skiprows=skiprows)
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            continue

        # Clean headers
        df.columns = df.iloc[0].astype(str)
        df = df[1:]
        df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

        # Update global order
        for col in df.columns:
            if col not in unified_cols:
                unified_cols.append(col)

        df["source_sheet"] = sheet
        all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    # Align columns across sheets
    aligned_frames = [df.reindex(columns=unified_cols + ["source_sheet"]) for df in all_frames]
    combined = pd.concat(aligned_frames, ignore_index=True)

    # ✅ Enforce required column order
    desired_order = [
        "year", "month", "day", "hour_of_year"
    ]

    # Add missing desired columns
    for col in desired_order:
        if col not in combined.columns:
            combined[col] = pd.NA

    # Final order = desired + other inputs + source_sheet
    other_cols = [c for c in combined.columns if c not in desired_order and c != "source_sheet"]
    final_order = desired_order + other_cols + ["source_sheet"]

    return combined.reindex(columns=final_order)
