from sqlmesh import model
import pandas as pd

PROGRAM_INPUT_COLUMNS = {
    "program_id": "int",
    "program_name": "string",
    "program_include": "string",
    "program_year": "int",
    "subsector": "string",
    "program_admin_costs_dollar_year": "float",
    "program_incentive_utility_dollar_year": "float",
    "program_performance_incentive_utility_dollar_year": "float",
    "program_federal_incentives_dollar_year": "float"
}


@model(
    name="nspm_input.program_inputs",
    kind="FULL",
    columns=PROGRAM_INPUT_COLUMNS
)
def program_inputs_model(*args, **kwargs) -> pd.DataFrame:
    df = (pd.read_excel('nspm/input/OpenBCA Code PROGRAM File.xlsx', sheet_name="Program Inputs", header=0)
    .rename(columns={
        "Program ID": "program_id",
        "Program Name": "program_name",
        "Program Include": "program_include",
        "Program Year": "program_year",
        "Subsector": "subsector",
        "Program Admin Costs ($-year)": "program_admin_costs_dollar_year",
        "Program Incentive Utility ($-year)": "program_incentive_utility_dollar_year",
        "Program Performance Incentive Utility ($-year)": "program_performance_incentive_utility_dollar_year",
        "Program Federal Incentives ($/year)": "program_federal_incentives_dollar_year"
    }, errors="raise"))

    return df[df["program_id"].notnull()]
