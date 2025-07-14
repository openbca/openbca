from sqlmesh import model
import pandas as pd

LOAD_SHAPE_MAPPING_HOURLY_COLUMNS = {
    "load_shape_name": "string",
    **{str(i): "float" for i in range(1, 8761)}
}


@model(
    name="loadshape_mapping_hourly",
    kind="FULL",
    columns=LOAD_SHAPE_MAPPING_HOURLY_COLUMNS
)
def loadshape_mapping_hourly_model() -> pd.DataFrame:
    df = pd.read_excel(
        'nspm/input/OpenBCA Code PROGRAM File.xlsx',
        sheet_name="Loadshape Mapping Hourly",
        header=1
    )

    df = df.rename(columns={"Loadshape Name": "load_shape_name"})

    # unpivot the DataFrame to have one row per hour
    df = df.melt(
        id_vars=["load_shape_name"],
        var_name="hour_of_year",
        value_name="value"
    )

    df = df[df["load_shape_name"].notna()]
    return df
