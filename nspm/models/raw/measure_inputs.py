from sqlmesh import model
import pandas as pd

MEASURE_INPUTS_COLUMNS = {
    "measure_id": "int",
    "program_name": "string",
    "measure_include": "string",
    "version": "string",
    "subset": "string",
    "measure_year": "int",
    "subsector": "string",
    "measure_name": "string",
    "measure_unit": "string",
    "loadshape_mapping": "string",
    "efficient_measure_life_years": "int",
    "measure_participation_number_year": "int",
    "measure_incremental_costs_customer_dollar_year": "float",
    "measure_annual_om_cost_customer_dollar_year": "float",
    "measure_one_time_incentive_utility_dollar_participant_year": "float",
    "measure_annual_incentive_utility_dollar_participant_year": "float",
    "administration_costs_dollar_year": "float",
    "measure_transaction_costs_dollar_participant_year": "float",
    "measure_interconnection_costs_dollar_participant_year": "float",
    "measure_tax_incentives_dollar_participant_year": "float",
    "measure_non_energy_impacts_dollar_participant_year": "float",
    "measure_non_energy_impacts_low_income_dollar_participant_year": "float"
}


@model(
    name="nspm_raw.measure_inputs",
    kind="FULL",
    columns=MEASURE_INPUTS_COLUMNS
)
def measure_inputs_model(*args, **kwargs) -> pd.DataFrame:
    df = pd.read_excel('nspm/input/OpenBCA Code PROGRAM File.xlsx', sheet_name="Measure Inputs", header=0)

    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Measure ID": "measure_id",
        "Program Name": "program_name",
        "Measure Include": "measure_include",
        "Version": "version",
        "Subset": "subset",
        "Measure Year": "measure_year",
        "Subsector": "subsector",
        "Measure Name": "measure_name",
        "Measure Unit": "measure_unit",
        "Loadshape Mapping": "loadshape_mapping",
        "Efficient Measure Life (years)": "efficient_measure_life_years",
        "Measure Participation (#-year)": "measure_participation_number_year",
        "Measure Incremental Costs - Customer ($) - year": "measure_incremental_costs_customer_dollar_year",
        "Measure Annual O&M Cost - Customer ($/year)" : "measure_annual_om_cost_customer_dollar_year",
        "Measure One Time Incentive Utility ($/participant-year)": "measure_one_time_incentive_utility_dollar_participant_year",
        "Measure Annual Incentive Utility ($/participant-year)": "measure_annual_incentive_utility_dollar_participant_year",
        "Administration Costs ($/year)": "administration_costs_dollar_year",
        "Measure Transaction Costs ($/participant-year)": "measure_transaction_costs_dollar_participant_year",
        "Measure Interconnection Costs ($/participant-year)": "measure_interconnection_costs_dollar_participant_year",
        "Measure Tax Incentives ($/participant-year)": "measure_tax_incentives_dollar_participant_year",
        "Measure Non-Energy Impacts ($/participant-year)": "measure_non_energy_impacts_dollar_participant_year",
        "Measure Non-Energy Impacts - Low-Income ($/participant-year)": "measure_non_energy_impacts_low_income_dollar_participant_year"
    }, errors="raise")

    df = df[df["measure_id"].notna()]
    return df
