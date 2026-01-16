from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd
import os
import re

ID_COLUMNS = ["id", "measure_id", "project_id"]

@model(
    name="openbca_input.measures",
    kind="FULL",
    grain=ID_COLUMNS,
    columns={
        "id": "string",
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
        "annual_electric_savings_kwh": "float",
        "coincident_peak_savings_kw": "float",
        "natural_gas_load_shape": "string",
        "annual_natural_gas_savings_mmbtu": "float",
        "annual_propane_savings_mmbtu": "float",
        "annual_oil_savings_mmbtu": "float",
        "annual_diesel_savings_mmbtu": "float",
        "estimated_useful_life": "int",
        "ntg": "float",
        "administration_costs_upfront_dollar_per_unit": "float",
        "administration_costs_annual_dollar_per_unit_year": "float",
        "utility_incentive_upfront_dollar_per_unit": "float",
        "utility_incentive_annual_dollar_per_unit_year": "float",
        "incremental_costs_upfront_dollar_per_unit": "float",
        "incremental_costs_annual_dollar_per_unit_year": "float",
        "host_customer_transaction_costs_dollar_per_unit": "float",
        "host_customer_interconnection_costs_dollar_per_unit": "float",
        "host_customer_tax_incentives_upfront_dollar_per_unit": "float",
        #"incremental_costs_upfront_per_unit_dollar": "float",
        #"incremental_costs_annual_per_unit_dollar_per_year": "float",
        #"utility_upfront_incentive_per_unit_dollar": "float",
        #"utility_annual_incentive_per_unit_dollar_per_year": "float",
        #"administration_costs_per_unit_dollar": "float",
        #"host_customer_transaction_costs_per_unit_dollar": "float",
        #"host_customer_interconnection_costs_per_unit_dollar": "float",
        #"host_customer_tax_incentives_per_unit_dollar": "float",
        "host_customer_non_energy_impacts_dollar_per_unit": "float",
        "host_customer_non_energy_impacts_low_income_dollar_per_unit": "float",
        "change_in_host_customer_risk_dollar_per_unit": "float",
        "change_in_host_customer_reliability_dollar_per_unit": "float",
        "change_in_host_customer_resilience_dollar_per_unit": "float",
        "change_in_societal_resilience_dollar_per_unit": "float",
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
        "label_1": "string",    
        "label_2": "string",
        "label_3": "string",
        "label_4": "string",
        "label_5": "string",
    },
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_measure_inputs_from_excel(
        input_file="OpenBCA Program Input.xlsx",
        sheet_name="Measure Inputs",
        skiprows=2
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
    sheet_name: str,
    skiprows: int
) -> DataFrame:
    """
    Load Measure Inputs sheet from Excel into a DataFrame.
    """
    file_path = os.path.join(DATA_DIR, input_file)

    # Read sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)

    # Apply header cleaning
    df.columns = [clean_header(c) for c in df.columns]

    # Rescale discount rate for use in NPV calculations
    # df['discount_rate'] = df['discount_rate']/100

    # Fill in null values of avoided cost subset with 'System-wide'

    df['avoided_cost_subset'].fillna('System-wide', inplace=True)

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

    df['annual_electric_savings_kwh'] = df.apply(lambda x: fill_savings_for_dimensioned_load_shapes(x['electric_load_shape'], x['annual_electric_savings_kwh']), axis = 1)
    
    df['annual_natural_gas_savings_mmbtu'] = df.apply(lambda x: fill_savings_for_dimensioned_load_shapes(x['natural_gas_load_shape'], x['annual_natural_gas_savings_mmbtu']), axis = 1)

    def load_value_stream_groups_from_excel(df) -> pd.DataFrame:
        '''
        Generate dataframe to classify value stream grouping from the Configuration Data sheet in the OpenBCA CONFIG file.
        '''
        file_path_config = os.path.join(DATA_DIR, 'OpenBCA Configuration.xlsm')
        xls_config = pd.ExcelFile(file_path_config)
        
        custom_avoided_cost_names_df = pd.read_excel(
            xls_config, 
            sheet_name='Configuration Data', 
            header=0, 
            skiprows=3, 
            usecols='C:D').tail(5)

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
            # 'annual_natural_gas_savings_mmbtu':'annual_natural_gas_mmbtu_savings',
            # 'annual_propane_savings_mmbtu':'annual_propane_mmbtu_savings',
            # 'annual_oil_savings_mmbtu':'annual_oil_mmbtu_savings',
            # 'annual_diesel_savings_mmbtu':'annual_diesel_mmbtu_savings'
        }, 
        axis = 1, inplace = True)

    return df