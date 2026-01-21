from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd
import os

@model(
    name='openbca_input.global_parameters',
    kind='FULL',
    columns={
        'real_or_nominal_inputs': 'string',
        'inflation_rate': 'float',
        'discount_rate': 'float',
        'discount_cadence': 'int',
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

real_nominal_row = 9
inflation_rate_row = 7
discount_rate_row = 9
discount_cadence_row = 10
line_losses_rows = [12, 13]
cost_treatment_row = 14

def compile_global_parameters_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to store global parameters from the Common Data sheet in the OpenBCA CONFIG file.
    '''
    file_path = os.path.join(DATA_DIR, input_file)
    xls = pd.ExcelFile(file_path)

    real_nominal_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != real_nominal_row, 
        usecols='B,C').T.reset_index()

    real_nominal_df.columns = ['real_or_nominal_inputs']
    real_nominal_df.drop([0], inplace=True)
    real_nominal_df['real_or_nominal_inputs'] = real_nominal_df['real_or_nominal_inputs'].apply(lambda x: 'nominal' if 'nominal' in x.lower() else 'real')


    inflation_rate_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != inflation_rate_row, 
        usecols='B,D').T.reset_index()

    inflation_rate_df.columns = ['inflation_rate']
    inflation_rate_df.drop([0], inplace=True)
    
    discount_rate_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != discount_rate_row, 
        usecols='B,D').T.reset_index()

    discount_rate_df.columns = ['discount_rate']
    discount_rate_df.drop([0], inplace=True)

    discount_cadence_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != discount_cadence_row, 
        usecols='B,C').T.reset_index()

    discount_cadence_dict = {'Annual': 1, 'Quarterly': 4}

    discount_cadence_df.columns = ['discount_cadence']
    discount_cadence_df.drop([0], inplace=True)
    discount_cadence_df['discount_cadence'] = discount_cadence_df['discount_cadence'].apply(lambda x: discount_cadence_dict[x])

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

    global_parameters_df = pd.concat([
        real_nominal_df.reset_index(drop=True),
        inflation_rate_df.reset_index(drop=True),
        discount_rate_df.reset_index(drop=True), 
        discount_cadence_df.reset_index(drop=True), 
        line_losses_df.reset_index(drop=True), 
        cost_treatment_df.reset_index(drop=True)
        ], axis = 1)

    return global_parameters_df