from typing import Any
from sqlmesh import model, ExecutionContext
import pandas as pd

from parsing_helper_functions import clean_header
from config.paths import get_input_templates_dir

@model(
    name="openbca_input.first_year_avoided_costs_by_id", 
    kind="FULL",
    columns={
        "id": "string",
        "year": "int",
        "value_stream": "string",
        "gross_dollar_value": "float",
    },
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    df = load_first_year_avoided_costs_from_excel(
        input_file="OpenBCA_Configuration.xlsm",
        first_year_avoided_costs_input_file="OpenBCA_Program_Input.xlsm",
    )
    if df.empty:
        yield from ()
    else:
        yield df

def load_first_year_avoided_costs_from_excel(
    input_file: str,
    first_year_avoided_costs_input_file: str,
) -> pd.DataFrame:

    """
    Generate dataframe to scrape first year avoided costs by id from the Configuration Data sheet of the Configuration file cross referencing the Measure Inputs sheet in the Program Input file.
    """

    first_year_avoided_costs_config_program_dict = {
        #'Host Customer Resilience':'Change in Host Customer Resilience',
        'Host Customer NEIs':'Host Customer Non-Energy Impacts Upfront ($)',
        #'Host Customer NEIs - LI ':'Host Customer Non-Energy Impacts - Low-Income Upfront ($)',
        'Host Customer NEIs - LI':'Host Customer Non-Energy Impacts - Low-Income Upfront ($)',
    }

    # Beginning with the Configuration Data sheet, filter for only the Value Streams that included in the test and are not adder (%) and with a calculation type of Measure-specific.

    file_path = get_input_templates_dir() / input_file
    xls = pd.ExcelFile(file_path, engine="calamine")

    first_year_avoided_costs_config_df = pd.read_excel(
        xls, 
        sheet_name='Configuration Data', 
        header=0, 
        skiprows=3, 
        usecols='C:I',
        engine="calamine",
        )[[
            'Value Stream',
            'Include in Test',
            'Data Granularity / Calculation Type',
            ]]

    first_year_avoided_costs_config_df = first_year_avoided_costs_config_df[
        first_year_avoided_costs_config_df['Value Stream'].isin(first_year_avoided_costs_config_program_dict.keys())
        & (first_year_avoided_costs_config_df['Include in Test'] == 'Yes')
        & (first_year_avoided_costs_config_df['Data Granularity / Calculation Type'] != 'Adder (%)')
        & (first_year_avoided_costs_config_df['Data Granularity / Calculation Type'] == 'Measure-specific')
    ] 

    first_year_avoided_costs = first_year_avoided_costs_config_df['Value Stream'].apply(lambda x: first_year_avoided_costs_config_program_dict[x]).unique().tolist()

    # Next, scrape the Measure Inputs sheet in the Program Input file for the first year avoided costs by id. Null out any values with configuration conflicts.
    first_year_avoided_costs_file_path = get_input_templates_dir() / first_year_avoided_costs_input_file
    first_year_avoided_costs_xls = pd.ExcelFile(first_year_avoided_costs_file_path, engine="calamine")

    first_year_avoided_costs_df = pd.read_excel(
        first_year_avoided_costs_xls,
        sheet_name='Measure Inputs',
        skiprows=3,
        engine="calamine",
    )[['Unique ID', 'Start Year']+first_year_avoided_costs].rename({'Unique ID':'id', 'Start Year':'year'}, axis=1)

    # Add in headers for any possible first year avoided costs that are treated elsewhere
    for cost in list(set(first_year_avoided_costs_config_program_dict.values())):
        if cost not in first_year_avoided_costs_df.columns:
            first_year_avoided_costs_df[cost] = None

    first_year_avoided_costs_df.columns = [clean_header(c) for c in first_year_avoided_costs_df.columns]

    long_dfs = []
    for col in first_year_avoided_costs_df.columns[2:]:
        df = first_year_avoided_costs_df[['id', 'year', col]].rename({col: 'gross_dollar_value'}, axis=1)
        df['value_stream'] = col
        long_dfs.append(df[['id', 'year', 'value_stream', 'gross_dollar_value']])

    first_year_avoided_costs_df = pd.concat(long_dfs).query('~gross_dollar_value.isnull()')

    if len(first_year_avoided_costs_df) == 0:
        first_year_avoided_costs_df = pd.DataFrame(columns=['id', 'year', 'value_stream', 'gross_dollar_value'])

    return first_year_avoided_costs_df