from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd

from config.paths import get_input_templates_dir

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

non_system_commodities = [
    'Host Customer Risk', 
    'Host Customer Reliability',
    'Host Customer Resilience',
    'Host Customer NEIs',
    'Host Customer NEIs - LI',
    'Societal Resilience'
    ]

config_cost_name_commodity_map_dict = {
    'Utility Program Admin Costs': 'ADMIN',
    'Utility Financial Incentives': 'UTILITY INCENTIVE',
    'Host Customer Incremental Cost': 'MEASURE COST',
    'Host Customer Transaction Cost': 'MEASURE COST',
    'Host Customer Interconn Cost': 'MEASURE COST',
    'Host Customer Tax Incentives': 'TAX INCENTIVE',
    'Program Level Benefits': 'NON-SYSTEM',
}

config_measure_cost_fields_map_dict = {
    'Utility Program Admin Costs': [
            'administration_costs_upfront_dollar',
            'administration_costs_annual_dollar_per_year',
            'program_admin_costs_dollar_per_year'
        ],
    'Utility Financial Incentives': [
            'utility_incentive_upfront_dollar',
            'utility_incentive_annual_dollar_per_year',
            'program_incentive_utility_to_customer_dollar_per_year',
            #'program_performance_incentive_govt_to_utility_dollar_per_year'
        ],
    'Host Customer Incremental Cost': [
            'incremental_costs_upfront_dollar',
            'incremental_costs_annual_dollar_per_year'
        ],
    'Host Customer Transaction Cost': [
        'host_customer_transaction_costs_dollar'
    ],        
    'Host Customer Interconn Cost': [
        'host_customer_interconnection_costs_dollar'
    ],
    'Host Customer Tax Incentives': [
            'host_customer_tax_incentive_upfront_dollar',
            #'program_federal_incentive_dollar_per_year'
        ],
    'Program Level Benefits': [
        'program_performance_incentive_govt_to_utility_dollar_per_year',
        'program_federal_incentive_dollar_per_year'
    ]
}

# Utility Performance Incentive
#program_performance_incentive_govt_to_utility_dollar_per_year
#program_federal_incentive_dollar_per_year

repeating_annual_costs = [
    'administration_costs_annual_dollar_per_year',
    'program_admin_costs_dollar_per_year', 
    'utility_incentive_annual_dollar_per_year',
    'incremental_costs_annual_dollar_per_year',
    'program_incentive_utility_to_customer_dollar_per_year',
    'program_performance_incentive_govt_to_utility_dollar_per_year',
    'program_federal_incentive_dollar_per_year'
    ]

def load_value_stream_groups_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to classify value stream grouping from the Configuration Data sheet in the OpenBCA CONFIG file.
    '''
    file_path = get_input_templates_dir() / input_file
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

    for col in column_headers:
        value_stream_groups_df[col] = value_stream_groups_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            
    value_stream_groups_df['include_in_test'] = value_stream_groups_df['include_in_test'].apply(lambda x: True if x == 'Yes' else False)

    def assign_value_stream_group(calc_type, commodity):
        
        if calc_type == None:
            return None

        elif calc_type == 'Adder (%)':
            if commodity == 'Electric':
                return 'electric_%_adder'
            elif commodity == 'Natural Gas':
                return 'natural_gas_%_adder'
            elif commodity == 'Propane':
                return 'propane_%_adder'
            elif commodity == 'Oil':
                return 'oil_%_adder'
            elif commodity == 'Diesel':
                return 'diesel_%_adder'
            else:
                return 'all_fuels_%_adder'

        elif calc_type == 'Peak Capacity - Annual':
            return 'capacity'

        elif calc_type == 'Single Value - First Year':
            return '$_adder'

        else:
            if commodity == 'Electric':
                return 'electric'
            if commodity == 'Natural Gas':
                return 'natural_gas'

            else:
                return 'annual'

    value_stream_groups_df['value_stream_group'] = value_stream_groups_df.apply(lambda x: assign_value_stream_group(x['calc_type'], x['commodity']), axis=1)
    value_stream_groups_df['commodity'] = value_stream_groups_df.apply(lambda x: x['avoided_cost'] if x['avoided_cost'] in non_system_commodities else x['commodity'], axis=1)

    value_stream_groups_costs_dfs = []
    for field in config_cost_name_commodity_map_dict.keys():

        if field == 'Program Level Benefits':
            include_in_test = True

        elif field in value_stream_groups_df['avoided_cost'].unique():
            include_in_test = value_stream_groups_df.query(f"avoided_cost == '{field}'")['include_in_test'].values[0]
            value_stream_groups_df = value_stream_groups_df.query(f"avoided_cost != '{field}'")
        
        else:
            include_in_test = False
            print(f"{field} not found in the configuration file.")

        for col in config_measure_cost_fields_map_dict[field]:

            df = pd.DataFrame(
                [[
                    col, 
                    config_cost_name_commodity_map_dict[field], 
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