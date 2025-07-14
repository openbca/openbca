from sqlmesh import model
import pandas as pd

CONFIG_INPUT_COLUMNS = {
    "base_year": "int",
    "program_year_1": "int",
    "program_end_year": "int",
    "inflation_rate": "float",
    "avg_line_losses_kwh": "float",
    "avg_line_losses_kw_peak": "float",
    "avg_line_losses_therm": "float",
    "reserve_margin": "float",
    "jurisdiction_test_pct": "float",
    "secondary_test_pct": "float"
}


@model(
    name="nspm_input.config_inputs",
    kind="FULL",
    columns=CONFIG_INPUT_COLUMNS
)
def config_inputs_model(*args, **kwargs) -> pd.DataFrame:
    df = pd.read_excel('nspm/input/OpenBCA Code CONFIG File.xlsx', sheet_name="Common Data", header=0)

    df = df.iloc[1:18, 0:2]
    df.columns = ["Input", "Value"]

    df = df.dropna(subset=["Input"]).reset_index(drop=True)

    df["Input"] = df["Input"].astype(str).str.strip()

    df = df.set_index("Input").T.reset_index(drop=True)

    df = df.rename(columns={
        "Base Year": "base_year",
        "Program Year 1": "program_year_1",
        "Program End Year": "program_end_year",
        "Inflation Rate": "inflation_rate",

        "Average Line Losses - kWh": "avg_line_losses_kwh",
        "Average Line Losses -  Peak kW": "avg_line_losses_kw_peak",
        "Average Line Losses - Gas Therm": "avg_line_losses_therm",
        "Reserve Margin": "reserve_margin",

        "Jurisdiction Specific Test, %": "jurisdiction_test_pct",
        "Secondary Test, %": "secondary_test_pct",
    }, errors="raise")

    return df
