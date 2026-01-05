from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd
import os

ID_COLUMNS = ['avoided_cost', 'commodity', 'include_in_test', 'calc_type', 'pct_adder', 'value_stream_group']

@model(
    name='openbca_input.value_stream_groups', 
    kind='FULL',
    grain=ID_COLUMNS,
    columns={
        'avoided_cost': 'string',
        'commodity': 'string',
        'include_in_test': 'boolean',
        'calc_type': 'string',
        'pct_adder': 'float',
        'value_stream_group': 'string'
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_value_stream_groups_from_excel(
        input_file='OpenBCA Configuration.xlsm'
    )

BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, '..', 'input_templates')  # adjust if needed

non_system_commodities = [
    'Host Customer Risk', 
    'Host Customer Reliability',
    'Host Customer Resilience',
    'Host Customer NEIs',
    'Host Customer NEIs - LI',
    'Societal Resilience'
    ]

config_cost_name_map_dict = {
    'Utility Program Admin Costs': 'ADMIN',
    'Utility Financial Incentives': 'INCENTIVE',
    'Host Customer Incremental Cost': 'MEASURE',
    'Host Customer Tax Incentives': 'TAX INCENTIVE'
}

config_cost_fields_map_dict = {
    'Utility Program Admin Costs': [
            'administration_costs_per_unit_dollar',
            'program_admin_costs_dollar_per_year'
        ],
    'Utility Financial Incentives': [
            'utility_upfront_incentive_per_unit_dollar',
            'utility_annual_incentive_per_unit_dollar_per_year',
            'program_incentive_utility_dollar_per_year',
            'program_performance_incentive_utility_dollar_per_year'
        ],
    'Host Customer Incremental Cost': [
            'incremental_costs_upfront_per_unit_dollar',
            # 'annual_o_m_cost_per_unit_dollar_per_year',
            'host_customer_transaction_costs_per_unit_dollar',
            'host_customer_interconnection_costs_per_unit_dollar'
        ],
    'Host Customer Tax Incentives': [
            'host_customer_tax_incentives_per_unit_dollar',
            'program_federal_incentives_dollar_per_year'
        ]
}

repeating_annual_costs = [
    'program_admin_costs_dollar_per_year', 
    'utility_annual_incentive_per_unit_dollar_per_year',
    'program_incentive_utility_dollar_per_year',
    'program_performance_incentive_utility_dollar_per_year',
    'program_federal_incentives_dollar_per_year'
    ]

def load_value_stream_groups_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to classify value stream grouping from the Configuration Data sheet in the OpenBCA CONFIG file.
    '''
    file_path = os.path.join(DATA_DIR, input_file)
    xls = pd.ExcelFile(file_path)
    
    value_stream_groups_df = pd.read_excel(
        xls, 
        sheet_name='Configuration Data', 
        header=0, 
        skiprows=3, 
        usecols='C:I')[[
            'Value Stream',
            'Commodity',
            'Include in Test',
            'Data Granularity / Calculation Type',
            'Adder (%)'
            ]]   

    column_headers = ['avoided_cost', 'commodity', 'include_in_test', 'calc_type', 'pct_adder']
    value_stream_groups_df.columns = column_headers

    print(value_stream_groups_df.dtypes)

    for col in column_headers:
        value_stream_groups_df[col] = value_stream_groups_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            
    value_stream_groups_df['include_in_test'] = value_stream_groups_df['include_in_test'].apply(lambda x: True if x == 'Yes' else False)

    def assign_value_stream_group(calc_type, commodity, avoided_cost):
        
        if calc_type == None:
            return None

        elif calc_type == 'Adder (%)':
            if commodity == 'Electric':
                return 'electric_%_adder'
            if commodity == 'Natural Gas':
                return 'natural_gas_%_adder'
            else:
                return 'all_fuels_%_adder'

        elif calc_type == 'Peak Capacity - Annual':
            return 'capacity'

        elif calc_type == 'Single Value - First Year':
            return '$_adder'

        elif commodity == 'Non-System' and avoided_cost in non_system_commodities:
            return avoided_cost

        else:
            if commodity == 'Electric':
                return 'electric'
            if commodity == 'Natural Gas':
                return 'natural_gas'

            else:
                return 'annual'

    value_stream_groups_df['value_stream_group'] = value_stream_groups_df.apply(lambda x: assign_value_stream_group(x['calc_type'], x['commodity'], x['avoided_cost']), axis=1)

    value_stream_groups_costs_dfs = []
    for field in config_cost_name_map_dict.keys():
        
        if field in value_stream_groups_df['avoided_cost'].unique():
            include_in_test = value_stream_groups_df.query(f"avoided_cost == '{field}'")['include_in_test'].values[0]
            value_stream_groups_df = value_stream_groups_df.query(f"avoided_cost != '{field}'")
        
        else:
            include_in_test = False
            print(f"{field} not found in the configuration file.")

        for col in config_cost_fields_map_dict[field]:

            df = pd.DataFrame(
                [[
                    col, 
                    config_cost_name_map_dict[field], 
                    include_in_test, 
                    'Time Series - Annual' if col in repeating_annual_costs else 'Single Value - First Year', 
                    None, 
                    'annual' if col in repeating_annual_costs else 'first_year'
                ]], 
                columns = [
                    'avoided_cost',
                    'commodity',
                    'include_in_test',
                    'calc_type',
                    'pct_adder',
                    'value_stream_group'
                ]
                )
            value_stream_groups_costs_dfs.append(df)

    value_stream_groups_costs_df = pd.concat(value_stream_groups_costs_dfs)

    value_stream_groups_df = pd.concat([value_stream_groups_df, value_stream_groups_costs_df])

    return value_stream_groups_df