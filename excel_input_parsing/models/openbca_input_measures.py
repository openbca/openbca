from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd

from parsing_helper_functions import clean_header
from config.paths import get_input_templates_dir

ID_COLUMNS = ["id", "measure_id", "project_id"]

input_file = "OpenBCA Program Input.xlsx"
sheet_name = "Measure Inputs"
file_path = get_input_templates_dir() / input_file
skiprows = 3

# Read sheet; use cleaned headers so MEASURES_SCHEMA_COLUMN_ORDER matches df.columns after clean_header()
with pd.ExcelFile(file_path, engine="calamine") as xls:
    custom_headers = [clean_header(c) for c in pd.read_excel(xls, sheet_name=sheet_name, skiprows=skiprows, nrows=1, engine="calamine").columns[2:7]]

# Column order must match the model schema below and the final returned dataframe.
MEASURES_SCHEMA_COLUMN_ORDER = [
    "id",
    "program_name",
    "measure_id",
    "project_id",
    "measure_name",
    "avoided_cost_subset",
    "start_year",
    "start_quarter",
    "discount_rate",
    "measure_unit",
    "unit_quantity",
    "estimated_useful_life",
    "ntg",
    "administration_costs_upfront_dollar",
    "administration_costs_annual_dollar_per_year",
    "utility_incentive_upfront_dollar",
    "utility_incentive_annual_dollar_per_year",
    "incremental_costs_upfront_dollar",
    "incremental_costs_annual_dollar_per_year",
    "host_customer_transaction_costs_dollar",
    "host_customer_interconnection_costs_dollar",
    "host_customer_tax_incentive_upfront_dollar",
    "electric_savings_load_shape",
    "annual_electric_savings_kwh",
    "coincident_peak_savings_kw",
    "natural_gas_savings_load_shape",
    "annual_natural_gas_savings_mmbtu",
    "annual_propane_savings_mmbtu",
    "annual_oil_savings_mmbtu",
    "annual_diesel_savings_mmbtu",
    "host_customer_non_energy_impacts_dollar",
    "host_customer_non_energy_impacts_low_income_dollar",
    "change_in_host_customer_risk_dollar",
    "change_in_host_customer_reliability_dollar",
    "change_in_host_customer_resilience_dollar",
    "change_in_societal_resilience_dollar",
    "custom_1_value_stream_name",
    "custom_1_value_stream_commodity",
    "custom_1_annual_savings",
    "custom_2_value_stream_name",
    "custom_2_value_stream_commodity",
    "custom_2_annual_savings",
    "custom_3_value_stream_name",
    "custom_3_value_stream_commodity",
    "custom_3_annual_savings",
    "custom_4_value_stream_name",
    "custom_4_value_stream_commodity",
    "custom_4_annual_savings",
    "custom_5_value_stream_name",
    "custom_5_value_stream_commodity",
    "custom_5_annual_savings",
] + custom_headers

columns={
    "id": "string",
    "program_name": "string",
    "measure_id": "string",
    "project_id": "string",
    "measure_name": "string",
    "avoided_cost_subset": "string",
    "start_year": "int",
    "start_quarter": "int",
    "discount_rate": "float", 
    "measure_unit": "string",
    "unit_quantity": "float",
    "estimated_useful_life": "int",
    "ntg": "float",
    "administration_costs_upfront_dollar": "float",
    "administration_costs_annual_dollar_per_year": "float",
    "utility_incentive_upfront_dollar": "float",
    "utility_incentive_annual_dollar_per_year": "float",
    "incremental_costs_upfront_dollar": "float",
    "incremental_costs_annual_dollar_per_year": "float",
    "host_customer_transaction_costs_dollar": "float",
    "host_customer_interconnection_costs_dollar": "float",
    "host_customer_tax_incentive_upfront_dollar": "float",
    "electric_savings_load_shape": "string",
    "annual_electric_savings_kwh": "float",
    "coincident_peak_savings_kw": "float",
    "natural_gas_savings_load_shape": "string",
    "annual_natural_gas_savings_mmbtu": "float",
    "annual_propane_savings_mmbtu": "float",
    "annual_oil_savings_mmbtu": "float",
    "annual_diesel_savings_mmbtu": "float",
    "host_customer_non_energy_impacts_dollar": "float",
    "host_customer_non_energy_impacts_low_income_dollar": "float",
    "change_in_host_customer_risk_dollar": "float",
    "change_in_host_customer_reliability_dollar": "float",
    "change_in_host_customer_resilience_dollar": "float",
    "change_in_societal_resilience_dollar": "float",
    "custom_1_value_stream_name": "string",
    "custom_1_value_stream_commodity": "string",
    "custom_1_annual_savings": "float", 
    "custom_2_value_stream_name": "string",
    "custom_2_value_stream_commodity": "string",
    "custom_2_annual_savings": "float", 
    "custom_3_value_stream_name": "string",
    "custom_3_value_stream_commodity": "string",
    "custom_3_annual_savings": "float", 
    "custom_4_value_stream_name": "string",
    "custom_4_value_stream_commodity": "string",
    "custom_4_annual_savings": "float", 
    "custom_5_value_stream_name": "string",
    "custom_5_value_stream_commodity": "string",
    "custom_5_annual_savings": "float", 
} 

for header in custom_headers:
    columns[header] = "string"

@model(
    name="openbca_input.measures",
    kind="FULL",
    grain=ID_COLUMNS,
    columns=columns,
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_measure_inputs_from_excel(
        input_file=input_file,
        sheet_name=sheet_name,
        skiprows=skiprows
    )


def load_measure_inputs_from_excel(
    input_file: str,
    sheet_name: str,
    skiprows: int
) -> DataFrame:
    """
    Load Measure Inputs sheet from Excel into a DataFrame.
    """
    file_path = get_input_templates_dir() / input_file

    # Read sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows, engine="calamine")

    # Apply header cleaning
    df.columns = [clean_header(c) for c in df.columns]

    # Fill in null values of avoided cost subset with 'System-wide'

    df['avoided_cost_subset'] = df['avoided_cost_subset'].fillna('System-wide')

    def fill_savings_for_dimensioned_load_shapes(load_shape_col: str, savings_col: float):
        """
        Check two values from dataframe columns:
        - If savings_col is not NaN/None, return it
        - Else if load_shape_col is not NaN/None/empty, return 1
        - Else return None
        """
        # Check if savings_col is valid (not NaN/None)
        if pd.notna(savings_col):
            return savings_col
        
        # Check if load_shape_col is valid (not NaN/None and not empty string)
        if pd.notna(load_shape_col) and (not isinstance(load_shape_col, str) or load_shape_col != ""):
            return 1
        
        # Both are invalid, return None (will become NaN in Pandas)
        return None

    df['annual_electric_savings_kwh'] = df.apply(lambda x: fill_savings_for_dimensioned_load_shapes(x['electric_savings_load_shape'], x['annual_electric_savings_kwh']), axis = 1)
    
    df['annual_natural_gas_savings_mmbtu'] = df.apply(lambda x: fill_savings_for_dimensioned_load_shapes(x['natural_gas_savings_load_shape'], x['annual_natural_gas_savings_mmbtu']), axis = 1)

    def load_value_stream_groups_from_excel(df) -> pd.DataFrame:
        '''
        Generate dataframe to classify value stream grouping from the Configuration Data sheet in the OpenBCA CONFIG file.
        '''
        file_path_config = get_input_templates_dir() / 'OpenBCA Configuration.xlsm'
        xls_config = pd.ExcelFile(file_path_config, engine="calamine")
        
        custom_avoided_cost_names_df = pd.read_excel(
            xls_config, 
            sheet_name='Configuration Data', 
            header=0, 
            skiprows=3, 
            usecols='C:D', 
            engine="calamine").tail(5)

        #value_stream_names = custom_avoided_cost_names_df[value_stream_col_name].to_list()
        custom_avoided_cost_names_df['Commodity'] = custom_avoided_cost_names_df['Commodity'].astype(str)

        value_stream_names_commodity_dict = dict(zip(custom_avoided_cost_names_df['Value Stream'], custom_avoided_cost_names_df['Commodity']))

        for i, (name, commodity) in enumerate(value_stream_names_commodity_dict.items()):
            df[f"custom_{i+1}_value_stream_name"] = name
            
            if commodity.upper() in ['ELECTRIC', 'NATURAL GAS', 'PROPANE', 'DIESEL', 'OIL', 'NON-SYSTEM', 'ALL FUELS', 'NAN']:
                df[f"custom_{i+1}_value_stream_commodity"] = f"STANDARD_{i+1}"
                df[f"custom_{i+1}_annual_savings"] = None
            else:
                df[f"custom_{i+1}_value_stream_commodity"] = commodity.upper()

        return df
    
    df = load_value_stream_groups_from_excel(df = df)

    df.rename(
        {
            'estimated_useful_life_years':'estimated_useful_life',
            'unique_id':'id'
        },
        axis=1,
        inplace=True,
    )

    # Enforce schema column order; KeyError if a schema column is missing from the Excel
    return df[MEASURES_SCHEMA_COLUMN_ORDER]