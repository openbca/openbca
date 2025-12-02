from typing import Any
#from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd
#from tabulate import tabulate
import os

@model(
    name='nspm.openbca_input_global_parameters',
    kind='FULL',
    #grain=ID_COLUMNS,
    columns={
        'discount_rate': 'float',
        'electric_line_loss': 'float',
        'natural_gas_line_loss': 'float',
        'cost_treatment': 'string',
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return compile_global_parameters_from_excel(
        input_file='OpenBCA Configuration.xlsm'
    )

BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, '..', 'input_templates')  # adjust if needed

discount_rate_row = 9
line_losses_rows = [12, 13]
cost_treatment_row = 15

def compile_global_parameters_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to store global parameters from the Common Data sheet in the OpenBCA CONFIG file.
    '''
    file_path = os.path.join(DATA_DIR, input_file)
    xls = pd.ExcelFile(file_path)
    
    discount_rate_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != discount_rate_row, 
        usecols='B,D').T.reset_index()

    discount_rate_df.columns = ['discount_rate']
    discount_rate_df.drop([0], inplace=True)

    line_losses_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x not in line_losses_rows, 
        usecols='D').T.reset_index()

    line_losses_df.columns = ['electric_line_loss', 'natural_gas_line_loss']

    cost_treatment_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != cost_treatment_row, 
        usecols='B,C').T.reset_index()

    cost_treatment_df.columns = ['cost_treatment']
    cost_treatment_df.drop([0], inplace=True)

    global_parameters_df = pd.concat([discount_rate_df.reset_index(drop=True), line_losses_df.reset_index(drop=True), cost_treatment_df.reset_index(drop=True)], axis = 1)
    
    return global_parameters_df