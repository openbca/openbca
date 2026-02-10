from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd

from config.paths import get_input_templates_dir

ID_COLUMNS = [
    "avoided_cost", "year", "quarter", "month", "day_of_year", "type_of_day",
    "hour_of_day", "hour_of_year"
]

@model(
    name="openbca_input.avoided_costs_ts", 
    kind="FULL",
    grain=ID_COLUMNS,
    columns={
        "avoided_cost": "string",
        "avoided_cost_subset": "string",
        "year": "int",
        "quarter": "int",
        "month": "int",
        "day_of_year": "int",
        "type_of_day": "string",
        "hour_of_day": "int",
        "hour_of_year": "int",
        "avoided_cost_value": "float",
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_avoided_costs_from_excel(
        input_file="OpenBCA Configuration.xlsm",
        skip_sheets={"Front Page", "Updates & Improvements", "Common Data", "Validations", "Configuration Data", "Dictionary"},
        skiprows=3
    )

def load_avoided_costs_from_excel(
    input_file: str,
    skip_sheets: set,
    skiprows: int = 2
) -> pd.DataFrame:
    """
    Load and consolidate timeseries data from an Excel workbook, enforce schema, and pivot to long format.
    """
    file_path = get_input_templates_dir() / input_file
    xls = pd.ExcelFile(file_path)

    def custom_period_to_hour_of_year_map():

        custom_period_df = pd.read_excel(
            xls, 
            sheet_name='Common Data', 
            usecols='C:Z', 
            skiprows=28
            ).reset_index().rename({'index':'month'}, axis=1)

        custom_period_df['month'] = custom_period_df['month'] + 1

        custom_period_df = pd.melt(custom_period_df, id_vars=['month'], value_vars=list(range(1,25)))

        custom_period_df.rename({'variable': 'hour_of_day', 'value': 'custom_period'}, inplace=True, axis = 1)
        custom_period_df['hour_of_day'] = custom_period_df['hour_of_day'] - 1 

        month_hod_hoy_map = pd.date_range('2023-01-01', periods=8760, freq='h')
        
        month_hod_hoy_map_df = pd.DataFrame({
            'month': month_hod_hoy_map.month,
            'hour_of_day': month_hod_hoy_map.hour,
            'hour_of_year': range(1, 8761)
        })

        custom_period_df = custom_period_df.merge(month_hod_hoy_map_df, on=['month', 'hour_of_day'])
        
        return custom_period_df.sort_values(by=['hour_of_year'])

    custom_period_df = custom_period_to_hour_of_year_map()

    all_frames = []
    unified_cols = []  # global column order (excluding metadata)

    for sheet in xls.sheet_names:
        if sheet in skip_sheets:
            continue

        # --- Find "Calculation Type" from row 2 ---
        avoided_cost = pd.read_excel(xls, sheet_name=sheet, header=None, skiprows=1, nrows=1, usecols='A').values[0][0]

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

        if 'custom_period' in df.columns:
            df = df.merge(custom_period_df, on = ['custom_period']).drop(['custom_period'], axis=1)

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
        "year", "quarter", "month", "day_of_year", "type_of_day",
        "hour_of_day", "hour_of_year"
    ]
    for col in desired_order:
        if col not in combined.columns:
            combined[col] = pd.NA

    # Final order = desired + other inputs + avoided_cost
    other_cols = [c for c in combined.columns if c not in desired_order and c not in ["avoided_cost"]]
    final_order = ["avoided_cost"] + desired_order + other_cols 
    combined = combined.reindex(columns=final_order)

    # ✅ Pivot to long format
    long_df = combined.melt(
        id_vars=ID_COLUMNS,
        value_vars=[c for c in combined.columns if c not in ID_COLUMNS],
        var_name="avoided_cost_subset",
        value_name="avoided_cost_value"
    ).dropna(axis=0, subset=['avoided_cost_value'])#.rename({'day': 'day_of_year'}, axis = 1)

    # Trim "Input" text if present
    long_df["avoided_cost_subset"] = long_df["avoided_cost_subset"].str.replace(" Inputs", "", regex=False)
    
    # Adjust hour_of_year from 1 - 8760 to 0 - 8759
    long_df['hour_of_year'] = long_df['hour_of_year'] - 1
    
    return long_df