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
        input_file='OpenBCA_Program_Input.xlsm'
    )

def load_program_value_streams_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to scrape program-level value streams grouping from the Program Inputs sheet in the OpenBCA_Program_Input.xlsm file.
    '''
    file_path =  get_input_templates_dir() / input_file
    xls = pd.ExcelFile(file_path, engine="calamine")
    
    program_value_streams_df = pd.read_excel(
        xls, 
        sheet_name='Program Inputs', 
        header=0, 
        skiprows=2,
        engine="calamine", 
        )

    program_value_streams_df.columns = [clean_header(c) for c in program_value_streams_df.columns]

    program_value_streams_df = program_value_streams_df[[
        'program_name', 
        'program_year',
        'program_admin_costs_dollar',
        'program_utility_incentive_dollar',
        'program_performance_incentive_to_utility_dollar',
        'program_federal_incentive_dollar'
        ]].melt(
        id_vars=['program_name', 'program_year'],
        value_vars=[        
            'program_admin_costs_dollar',
            'program_utility_incentive_dollar',
            'program_performance_incentive_to_utility_dollar',
            'program_federal_incentive_dollar'
            ],
        var_name="avoided_cost",
        value_name="avoided_cost_value"
    ).dropna(axis=0, subset=['avoided_cost_value'])

    return program_value_streams_df