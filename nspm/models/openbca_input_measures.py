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
        "unique_row_id": "string",
        "measure_id": "string",
        "project_id": "string",
        "program_name": "string",
        "measure_include": "string",
        "version": "string",
        "avoided_cost_subset": "string",
        "start_year": "int",
        "start_quarter": "int",
        "discount_rate": "float", 
        "measure_name": "string",
        "measure_unit": "string",
        "unit_quantity": "float",
        "electric_load_shape": "string",
        "annual_kwh_impact": "float",
        "coincident_peak_kw_impact": "float",
        "natural_gas_load_shape": "string",
        "annual_natural_gas_impact_mmbtu": "float",
        "annual_other_fuel_propane_mmbtu": "float",
        "annual_other_fuel_heating_oil_mmbtu": "float",
        "annual_other_fuel_diesel_mmbtu": "float",
        "estimated_useful_life_years": "int",
        "ntg": "float",
        "incremental_costs_upfront_per_unit_dollar": "float",
        "annual_o_m_cost_per_unit_dollar_per_year": "float",
        "utility_upfront_incentive_per_unit_dollar": "float",
        "utility_annual_incentive_per_unit_dollar_per_year": "float",
        "administration_costs_per_unit_dollar": "float",
        "host_customer_transaction_costs_per_unit_dollar": "float",
        "host_customer_interconnection_costs_per_unit_dollar": "float",
        "host_customer_tax_incentives_per_unit_dollar": "float",
        "host_customer_non_energy_impacts_per_unit_dollar": "float",
        "host_customer_non_energy_impacts_low_income_per_unit_dollar": "float",
        "change_in_host_customer_reliability_per_unit": "float",
        "change_in_host_customer_resilience_per_unit": "float",
        "change_in_societal_resilience_per_unit": "float",
        "custom_v1": "string",
        "custom_v2": "string", 
        "custom_v3": "string",
        "custom_v4": "string",
        "custom_v5": "string",
        "label_1": "string",    
        "label_2": "string",
        "label_3": "string",
        "label_4": "string",
        "label_5": "string",
    },
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_measure_inputs_from_excel(
        input_file="OpenBCA Code PROGRAM INPUT.xlsx",
        sheet_name="Measure Inputs"
    )


BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, "..", "input_templates")  # adjust if needed

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

    for col in df.columns:
        print(col)

    print('\n\n')
    print(df.head(3))

    return df
 