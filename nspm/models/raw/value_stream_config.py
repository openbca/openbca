from sqlmesh import model
import pandas as pd

VALUE_STREAM_CONFIG_COLUMNS = {
    "value_stream": "string",
    "calculation_type": "string",
}


@model(
    name="nspm_raw.value_stream_config",
    kind="FULL",
    columns=VALUE_STREAM_CONFIG_COLUMNS
)
def value_stream_config_model(*args, **kwargs) -> pd.DataFrame:
    df = pd.read_excel(
        'nspm/input/OpenBCA Code INPUT File.xlsx',
        sheet_name="Data from CONFIG",
        header=1
    )

    df.columns = df.columns.str.strip()

    # skip the first 2 rows and keep only the first 2 columns
    df = df.iloc[2:, :2]
    df.columns = ["value_stream", "calculation_type"]
    df = df.dropna(subset=["value_stream", "calculation_type"])

    return df
