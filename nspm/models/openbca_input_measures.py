from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd
import os
import re

ID_COLUMNS = ["unique_row_id", "measure_id", "project_id"]
@model(
    name="nspm.openbca_input_measures",
    kind="FULL",
    grain=ID_COLUMNS,
    columns={
        "unique_row_id": "int",  
        "measure_id": "string",
        "project_id": "string",
        "program_name": "string",
        "measure_include": "string",
        "version": "string",
        "subset": "string",
        "start_year": "int",
        "start_quarter": "string",
        "measure_name": "string",
        "measure_unit": "string",
        "unit_quantity": "float",
        "loadshape_mapping": "string",
        "annual_kwh_impact": "float",
        "peak_kw_impact": "float",
        "annual_ng_impact_mmbtu": "float",
        "annual_other_fuels_impact_mmbtu": "float",
        "estimated_useful_life_years": "int",
        "ntg": "float",
        "measure_incremental_costs_per_unit_dollar": "float",
        "measure_annual_o_m_cost_per_unit_dollar_per_year": "float",
        "measure_one_time_incentive_utility_per_unit_dollar_per_year": "float",
        "measure_annual_incentive_utility_per_unit_dollar_per_year": "float",
        "administration_costs_dollar_per_year": "float",
        "measure_transaction_costs_per_unit_dollar_per_year": "float",
        "measure_interconnection_costs_per_unit_dollar_per_year": "float", 
        "measure_tax_incentives_per_unit_dollar_per_year": "float",
        "measure_non_energy_impacts_per_unit_dollar_per_year": "float",
        "measure_non_energy_impacts_low_income_per_unit_dollar_per_year": "float",
        "change_in_host_customer_reliability_customer_minute_outages_cmo": "float", 
        "custom_1_subsector": "string",
        "custom_2_zip_code": "string",
        "custom_3": "string",
        "custom_4": "string", 
        "custom_5": "string",
    },
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_measure_inputs_from_excel(
        input_file="OpenBCA Code PROGRAM INPUT.xlsx",
        sheet_name="Measure Inputs"
    )


BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, "..", "Input")  # adjust if needed

def clean_header(col: str) -> str:
    col = str(col).strip().lower()

    # Replace spaces, hyphens with underscore
    col = col.replace(" ", "_").replace("-", "_")

    # Remove parentheses
    col = re.sub(r"[()]", "", col)

    # Replace : and & with _
    col = col.replace(":", "_").replace("&", "_")

    # Replace $/ with _dollar_per_
    col = col.replace("$/", "_dollar_per_")

    # Replace $ with _dollar_
    col = col.replace("$", "_dollar_")

    # Collapse multiple underscores
    col = re.sub(r"__+", "_", col)

    # Strip trailing/leading underscores
    col = col.strip("_")

    return col

def load_measure_inputs_from_excel(
    input_file: str,
    sheet_name: str
) -> DataFrame:
    """
    Load Measure Inputs sheet from Excel into a DataFrame.
    """
    file_path = os.path.join(DATA_DIR, input_file)

    # Read sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Apply header cleaning
    df.columns = [clean_header(c) for c in df.columns]

    return df
