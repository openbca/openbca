from sqlmesh import model
import pandas as pd

LOAD_SHAPE_MAPPING_ANNUAL_COLUMNS = {
    "load_shape_name": "string",
    "year_ref": "string",
    "load_shape_normalized_fraction": "float",
}


@model(
    name="loadshape_mapping_annual",
    kind="FULL",
    columns=LOAD_SHAPE_MAPPING_ANNUAL_COLUMNS
)
def loadshape_mapping_annual_model() -> pd.DataFrame:
    df = pd.read_excel(
        'nspm/input/OpenBCA Code PROGRAM File.xlsx',
        sheet_name="Loadshape Mapping Annual",
        header=1
    )

    df = df.rename(columns={"Load Shape Name": "load_shape_name"}, errors="raise")

    # Filter out rows where first value is NaN
    df = df[df[df.columns[1]].notna()]

    df = df.melt(
        id_vars=["load_shape_name"],
        var_name="year_ref",
        value_name="load_shape_normalized_fraction"
    )

    df = df[df["load_shape_name"].notna()]
    return df
