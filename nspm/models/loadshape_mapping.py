from sqlmesh import model
import pandas as pd

@model(
    name="loadshape_mapping",
    kind="FULL",
    columns={
        "load_shape_name": "string",
        **{str(i): "float" for i in range(1, 8761)}
    }
)
def loadshape_mapping_hourly() -> pd.DataFrame:
    df = pd.read_excel(
        'nspm/input/OpenBCA Code PROGRAM File.xlsx',
        sheet_name="Loadshape Mapping Hourly",
        header=1
    )

    df = df.rename(columns=lambda col: (
        str(col).strip().lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
        .replace("$", "dollar")
        .strip("_")
    ))

    df = df[df["load_shape_name"].notna()]
    return df
