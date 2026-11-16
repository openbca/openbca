from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd

from config.paths import get_input_templates_dir

@model(
    name='openbca_input.load_shape_normalization',
    kind='FULL',
    columns={
        'impact_category': 'string',
        'load_shape': 'string',
        'normalized': 'boolean',
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return compile_ls_normalization_from_excel(
        input_file='OpenBCA_Program_Input.xlsm'
    )

sheet_name = 'Define Load Shape Names'
ls_table_start_row = 11

def compile_ls_normalization_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to store load shape normalization assignments from the Define Load Shape Names sheet in the OpenBCA Program Inputs file.
    '''
    file_path = get_input_templates_dir() / input_file
    xls = pd.ExcelFile(file_path, engine="calamine")

    electric_ls_df = pd.read_excel(
        xls, 
        sheet_name=sheet_name, 
        header=0, 
        skiprows=ls_table_start_row-1, 
        usecols='B,C',
        engine="calamine").dropna()

    electric_ls_df['impact_category'] = 'Electric'

    electric_ls_df.columns = ['load_shape', 'normalized', 'impact_category']
    electric_ls_df['normalized'] = electric_ls_df['normalized'].apply(lambda x: True if '%' in x else False)

    ng_ls_df = pd.read_excel(
        xls, 
        sheet_name=sheet_name, 
        header=0, 
        skiprows=ls_table_start_row-1, 
        usecols='F,G',
        engine="calamine").dropna()

    ng_ls_df['impact_category'] = 'Natural Gas'

    ng_ls_df.columns = ['load_shape', 'normalized', 'impact_category']
    ng_ls_df['normalized'] = ng_ls_df['normalized'].apply(lambda x: True if '%' in x else False)

    ls_normalization_df = pd.concat([electric_ls_df, ng_ls_df])

    if len(ls_normalization_df) == 0:
        return pd.DataFrame(columns=['impact_category', 'load_shape', 'normalized'])

    return ls_normalization_df[['impact_category', 'load_shape', 'normalized']]