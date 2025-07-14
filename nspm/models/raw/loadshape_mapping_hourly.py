from sqlmesh import model
import pandas as pd

LOAD_SHAPE_MAPPING_HOURLY_COLUMNS = {
    "load_shape_name": "string",
    "hour_of_year": "int",
    "load_shape_normalized_fraction": "float",
}


@model(
    name="nspm_raw.loadshape_mapping_hourly",
    kind="FULL",
    columns=LOAD_SHAPE_MAPPING_HOURLY_COLUMNS
)
def loadshape_mapping_hourly_model() -> pd.DataFrame:
    df = pd.read_excel(
        'nspm/input/OpenBCA Code PROGRAM File.xlsx',
        sheet_name="Loadshape Mapping Hourly",
        header=1
    )

    df = df.rename(columns={"Load Shape Name": "load_shape_name"}, errors="raise")

    # Filter out rows where first value is NaN
    df = df[df[df.columns[1]].notna()]

    df = df.melt(
        id_vars=["load_shape_name"],
        var_name="hour_of_year",
        value_name="load_shape_normalized_fraction"
    )

    df = df[df["load_shape_name"].notna()]
    return df
