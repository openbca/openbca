from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd

from config.paths import get_input_templates_dir

ID_COLUMNS = ['avoided_cost', 'impact_category', 'include_in_test', 'calc_type', 'pct_adder', 'value_stream_group']

@model(
    name='openbca_input.value_stream_groups', 
    kind='FULL',
    grain=ID_COLUMNS,
    columns={
        'avoided_cost': 'string',
        'impact_category': 'string',
        'include_in_test': 'boolean',
        'calc_type': 'string',
        'pct_adder': 'float',
        'value_stream_group': 'string',
        'marginal_ghg': 'boolean',
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_value_stream_groups_from_excel(
        input_file='OpenBCA_Configuration.xlsm'
    )

non_system_commodities = [
    'Host Customer Resilience',
    'Host Customer NEIs',
    'Host Customer NEIs - LI',
    'Societal Resilience',
    'Utility Credit & Collection',
    ]

config_cost_name_impact_category_map_dict = {
    'Utility Program Admin Costs': 'ADMIN',
    'Utility Direct Investment in DERs': 'ADMIN',
    'Utility Financial Incentives': 'UTILITY INCENTIVE',
    'Host Customer Incremental Cost': 'MEASURE COST',
    'Host Customer Transaction Cost': 'MEASURE COST',
    'Host Customer Interconnection Cost': 'MEASURE COST',
    'Host Customer Tax Incentives': 'TAX INCENTIVE',
    'Program Level Benefits': 'NON-SYSTEM',
}

config_measure_cost_fields_map_dict = {
    'Utility Program Admin Costs': [
            'admin_cost_upfront_dollar',
            'admin_cost_annual_dollar_per_year',
            'program_admin_costs_dollar',
        ],
    'Utility Direct Investment in DERs': [
            'utility_direct_investment_in_ders_dollar',
        ],
    'Utility Financial Incentives': [
            'utility_incentive_upfront_dollar',
            'utility_incentive_annual_dollar_per_year',
            'program_utility_incentive_dollar',
        ],
    'Host Customer Incremental Cost': [
            'incremental_cost_upfront_dollar',
            'incremental_cost_annual_dollar_per_year'
        ],
    'Host Customer Transaction Cost': [
        'host_customer_transaction_cost_dollar'
    ],        
    'Host Customer Interconnection Cost': [
        'host_customer_interconnection_cost_dollar'
    ],
    'Host Customer Tax Incentives': [
            'host_customer_tax_incentive_upfront_dollar',
        ],
    'Program Level Benefits': [
        'program_performance_incentive_to_utility_dollar',
        'program_federal_incentive_dollar'
    ]
}

repeating_annual_costs = [
    'admin_cost_annual_dollar_per_year',
    'program_admin_costs_dollar_per_year', 
    'utility_incentive_annual_dollar_per_year',
    'incremental_cost_annual_dollar_per_year',
    ]

marginal_ghg_value_streams = [
    'GHG Intensity (E)',
    'GHG Intensity (NG)',
    'GHG Intensity (Propane)',
    'GHG Intensity (Oil)',
    'GHG Intensity (Diesel)',
    'GHG Intensity (Wood)',
]

_VALUE_STREAM_GROUP_COLS = [
    'avoided_cost',
    'impact_category',
    'include_in_test',
    'calc_type',
    'pct_adder',
    'value_stream_group',
    'marginal_ghg',
]


def load_value_stream_groups_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to classify value stream grouping from the Configuration Data sheet in the OpenBCA CONFIG file.
    '''
    file_path = get_input_templates_dir() / input_file
    xls = pd.ExcelFile(file_path, engine="calamine")
    
    value_stream_groups_df = pd.read_excel(
        xls, 
        sheet_name='Configuration Data', 
        header=0, 
        skiprows=3, 
        usecols='C:I',
        engine="calamine",
        )[[
            'Value Stream',
            'Impact Category',
            'Include in Test',
            'Data Granularity / Calculation Type',
            'Adder (%)'
            ]]   

    column_headers = ['avoided_cost', 'impact_category', 'include_in_test', 'calc_type', 'pct_adder']
    value_stream_groups_df.columns = column_headers

    for col in column_headers:
        value_stream_groups_df[col] = value_stream_groups_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            
    value_stream_groups_df['include_in_test'] = value_stream_groups_df['include_in_test'].apply(lambda x: True if x == 'Yes' else False)
    value_stream_groups_df['pct_adder'] = pd.to_numeric(
        value_stream_groups_df['pct_adder'], errors='coerce'
    ).astype('Float64')

    def assign_value_stream_group(calc_type, impact_category):
        
        if calc_type == None:
            return None

        elif calc_type == 'Adder (%)':
            if impact_category == 'Electric':
                return 'electric_%_adder'
            elif impact_category == 'Natural Gas':
                return 'natural_gas_%_adder'
            elif impact_category == 'Propane':
                return 'propane_%_adder'
            elif impact_category == 'Oil':
                return 'oil_%_adder'
            elif impact_category == 'Diesel':
                return 'diesel_%_adder'
            elif impact_category == 'Wood':
                return 'wood_%_adder'
            else:
                return 'all_fuels_%_adder'

        elif calc_type == 'Peak Capacity - Annual':
            return 'capacity'

        elif calc_type == 'Measure-specific':#'Single Value - First Year': 
            print(f"impact_category: {impact_category}, calc_type: {calc_type}")
            return 'single_value_first_year'#'annual'

        else:
            if impact_category == 'Electric':
                return 'electric'
            if impact_category == 'Natural Gas':
                return 'natural_gas'
            else:
                return 'annual'

    value_stream_groups_df['value_stream_group'] = value_stream_groups_df.apply(lambda x: assign_value_stream_group(x['calc_type'], x['impact_category']), axis=1)
    value_stream_groups_df['impact_category'] = value_stream_groups_df.apply(lambda x: x['avoided_cost'] if x['avoided_cost'] in non_system_commodities else x['impact_category'], axis=1)
    value_stream_groups_df['marginal_ghg'] = value_stream_groups_df.apply(lambda x: True if x['avoided_cost'] in marginal_ghg_value_streams else False, axis=1)

    value_stream_groups_costs_dfs = []

    for field in config_cost_name_impact_category_map_dict.keys():

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
                    config_cost_name_impact_category_map_dict[field], 
                    include_in_test, 
                    'Time Series - Annual' if col in repeating_annual_costs else 'Single Value - First Year', 
                    pd.NA, 
                    'annual' if col in repeating_annual_costs else 'first_year',
                    False,
                ]], 
                columns=_VALUE_STREAM_GROUP_COLS,
            )
            value_stream_groups_costs_dfs.append(df)

    cost_blocks = [d for d in value_stream_groups_costs_dfs if not d.empty]
    if not cost_blocks:
        return value_stream_groups_df

    value_stream_groups_costs_df = pd.concat(cost_blocks, ignore_index=True)

    for col in _VALUE_STREAM_GROUP_COLS:
        if col in value_stream_groups_costs_df.columns and col in value_stream_groups_df.columns:
            value_stream_groups_costs_df[col] = value_stream_groups_costs_df[col].astype(
                value_stream_groups_df[col].dtype,
                copy=False,
            )

    value_stream_groups_df = pd.concat(
        [value_stream_groups_df, value_stream_groups_costs_df],
        ignore_index=True,
    )

    return value_stream_groups_df