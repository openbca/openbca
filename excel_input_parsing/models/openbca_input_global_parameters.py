from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd

from config.paths import get_input_templates_dir

@model(
    name='openbca_input.global_parameters',
    kind='FULL',
    columns={
        'inflation_rate': 'float',
        'dollar_year': 'int',
        'discount_rate': 'float',
        'discount_cadence': 'int',
        'electric_line_loss': 'float',
        'peak_capacity_line_loss': 'float',
        'natural_gas_line_loss': 'float',
        'cost_treatment': 'string',
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return compile_global_parameters_from_excel(
        input_file='OpenBCA Configuration.xlsm'
    )

real_nominal_row = 9
inflation_rate_row = 7
dollar_year_row = 4
discount_rate_row = 9
discount_cadence_row = 10
line_losses_rows = [12, 13, 14]
cost_treatment_row = 15

def compile_global_parameters_from_excel(
    input_file: str,
) -> pd.DataFrame:
    '''
    Generate dataframe to store global parameters from the Common Data sheet in the OpenBCA CONFIG file.
    '''
    file_path = get_input_templates_dir() / input_file
    xls = pd.ExcelFile(file_path, engine="calamine")

    real_nominal_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != real_nominal_row, 
        usecols='B,C',
        engine="calamine").T.reset_index()

    real_nominal_df.columns = ['real_inputs']
    real_nominal_df.drop([0], inplace=True)
    real_nominal_df['real_inputs'] = real_nominal_df['real_inputs'].apply(lambda x: False if 'nominal' in x.lower() else True)

    inflation_rate_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != inflation_rate_row, 
        usecols='B,D',
        engine="calamine").T.reset_index()

    inflation_rate_df.columns = ['inflation_rate']
    inflation_rate_df.drop([0], inplace=True)

    dollar_year_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != dollar_year_row, 
        usecols='B,D',
        engine="calamine").T.reset_index()

    dollar_year_df.columns = ['dollar_year']
    dollar_year_df.drop([0], inplace=True)

    discount_rate_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != discount_rate_row, 
        usecols='B,D',
        engine="calamine").T.reset_index()

    discount_rate_df.columns = ['discount_rate']
    discount_rate_df.drop([0], inplace=True)

    discount_cadence_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != discount_cadence_row, 
        usecols='B,C',
        engine="calamine").T.reset_index()

    discount_cadence_dict = {'Annual': 1, 'Quarterly': 4}

    discount_cadence_df.columns = ['discount_cadence']
    discount_cadence_df.drop([0], inplace=True)
    discount_cadence_df['discount_cadence'] = discount_cadence_df['discount_cadence'].apply(lambda x: discount_cadence_dict[x])

    line_losses_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x not in line_losses_rows, 
        usecols='D',
        engine="calamine").T.reset_index()

    line_losses_df.columns = ['electric_line_loss', 'peak_capacity_line_loss', 'natural_gas_line_loss']

    cost_treatment_df = pd.read_excel(
        xls, 
        sheet_name='Common Data', 
        header=0, 
        skiprows=lambda x: x != cost_treatment_row, 
        usecols='B,C',
        engine="calamine").T.reset_index()

    cost_treatment_df.columns = ['cost_treatment']
    cost_treatment_df.drop([0], inplace=True)

    global_parameters_df = pd.concat([
        real_nominal_df.reset_index(drop=True),
        inflation_rate_df.reset_index(drop=True),
        dollar_year_df.reset_index(drop=True),
        discount_rate_df.reset_index(drop=True), 
        discount_cadence_df.reset_index(drop=True), 
        line_losses_df.reset_index(drop=True), 
        cost_treatment_df.reset_index(drop=True)
        ], axis = 1)

    global_parameters_df['inflation_rate'] = global_parameters_df['real_inputs'].apply(lambda x: 0.0 if x else global_parameters_df['inflation_rate'])
    global_parameters_df.drop(columns=['real_inputs'], inplace=True)

    return global_parameters_df