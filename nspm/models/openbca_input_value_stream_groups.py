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
            'Commodity' ,
            'Include in Test',
            'Data Granularity / Calculation Type',
            'Adder (%)'
            ]]   

    value_stream_groups_df.columns = ['avoided_cost', 'commodity', 'include_in_test', 'calc_type', 'pct_adder']

    value_stream_groups_df['include_in_test'] = value_stream_groups_df['include_in_test'].apply(lambda x: True if x == 'Yes' else False)

    def assign_value_stream_group(calc_type, commodity):

        if calc_type == None:
            return None

        if calc_type == 'Adder (%)':
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

        else:
            if commodity == 'Electric':
                return 'electric'
            if commodity == 'Natural Gas':
                return 'natural_gas'
            else:
                return 'annual'

    value_stream_groups_df['value_stream_group'] = value_stream_groups_df.apply(lambda x: assign_value_stream_group(x['calc_type'], x['commodity']), axis=1)

    return value_stream_groups_df