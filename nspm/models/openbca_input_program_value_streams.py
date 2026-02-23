from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd

from parsing_helper_functions import clean_header
from config.paths import get_input_templates_dir

ID_COLUMNS = ['program_name', 'year']
 
@model(
    name='openbca_input.program_value_streams', 
    kind='FULL',
    grain=ID_COLUMNS,
    columns={
        'program_name': 'string',
        'program_year': 'int',
        'avoided_cost': 'string',
        'avoided_cost_value': 'float',
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_program_value_streams_from_excel(
        input_file='OpenBCA Program Input.xlsx'
    )

def load_program_value_streams_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to scrape program-level value streams grouping from the Program Inputs sheet in the OpenBCA Program Input.xlsx file.
    '''
    file_path =  get_input_templates_dir() / input_file
    xls = pd.ExcelFile(file_path)
    
    program_value_streams_df = pd.read_excel(
        xls, 
        sheet_name='Program Inputs', 
        header=0, 
        skiprows=2, 
        )

    program_value_streams_df.columns = [clean_header(c) for c in program_value_streams_df.columns]

    program_value_streams_df = program_value_streams_df[[
        'program_name', 
        'program_year',
        'program_admin_costs_dollar_per_year',
        'program_incentive_utility_to_customer_dollar_per_year',
        'program_performance_incentive_govt_to_utility_dollar_per_year',
        'program_federal_incentive_dollar_per_year'
        ]].melt(
        id_vars=['program_name', 'program_year'],
        value_vars=[        
            'program_admin_costs_dollar_per_year',
            'program_incentive_utility_to_customer_dollar_per_year',
            'program_performance_incentive_govt_to_utility_dollar_per_year',
            'program_federal_incentive_dollar_per_year'
            ],
        var_name="avoided_cost",
        value_name="avoided_cost_value"
    ).dropna(axis=0, subset=['avoided_cost_value'])

    return program_value_streams_df