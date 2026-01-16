from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd
import os
from parsing_helper_functions import clean_header

ID_COLUMNS = ['program_name', 'year']

@model(
    name='openbca_input.program_value_streams', 
    kind='FULL',
    grain=ID_COLUMNS,
    columns={
        'program_name': 'string',
        'program_year': 'int',
        'program_admin_costs_dollar_per_year': 'float',
        'program_incentive_utility_dollar_per_year': 'float',
        'program_performance_incentive_utility_dollar_per_year': 'float',
        'program_federal_incentives_dollar_per_year': 'float'

    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return load_program_value_streams_from_excel(
        input_file='OpenBCA Program Input.xlsx'
    )

BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, '..', 'input_templates')  # adjust if needed

def load_program_value_streams_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to scrape program-level value streams grouping from the Program Inputs sheet in the OpenBCA Program Input.xlsx file.
    '''
    file_path = os.path.join(DATA_DIR, input_file)
    xls = pd.ExcelFile(file_path)
    
    program_value_streams_df = pd.read_excel(
        xls, 
        sheet_name='Program Inputs', 
        header=0, 
        skiprows=2, 
        )

    program_value_streams_df.columns = [clean_header(c) for c in program_value_streams_df.columns]

    return program_value_streams_df[[
        'program_name', 
        'program_year',
        'program_admin_costs_dollar_per_year',
        'program_incentive_utility_dollar_per_year',
        'program_performance_incentive_utility_dollar_per_year',
        'program_federal_incentives_dollar_per_year'
        ]]