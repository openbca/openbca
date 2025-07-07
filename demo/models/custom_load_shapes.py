from typing import Any

from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd

ID_COLUMNS = {'sheet_name', 'month', 'hour_of_year', 'hour_of_week', 'hour_of_day'}

@model(
    name='demo.custom_load_shapes',
    kind='FULL',
    grain=('month', 'hour_of_year', 'load_shape'),
    columns = {
        'load_shape': 'string',
        'commodity': 'string',
        'quarter': 'int',
        'month': 'int',
        'hour_of_day': 'int',
        'hour_of_week': 'int',
        'hour_of_year': 'int',
        'value': 'float',
        'sheet_name': 'string'
    }
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return pd.concat([
            load_custom_load_shapes('ELECTRICITY', 'custom_electric_load_shapes.xlsx'),
            load_custom_load_shapes('GAS', 'custom_gas_load_shapes.xlsx'),
        ])


def load_custom_load_shapes(commodity: str, input_file: str) -> DataFrame:
    sheets_dict = pd.read_excel(pd.ExcelFile(f"demo/data/{input_file}"), sheet_name=None)
    df = (
        pd.concat([df.assign(sheet_name=sheet) for sheet, df in sheets_dict.items()], ignore_index=True)
    )
    for col in ID_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = (
        df
        .melt(
            id_vars=ID_COLUMNS,
            value_vars=[
                col for col in df.columns if col not in ID_COLUMNS
            ],
            var_name='load_shape',
            value_name='value'
        )
        .assign(commodity=commodity)
        .assign(quarter=lambda x: (x['month'] - 1) // 3 + 1)
    )

    df['load_shape'] = df['load_shape'].str.upper()

    return df
