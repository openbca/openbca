from typing import Any

from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd

ID_COLUMNS = ['utility', 'quarter', 'month', 'hour_of_year', 'hour_of_day']

@model(
    name='california.elec_load_shape_unpivoted',
    kind='FULL',
    grain=(*ID_COLUMNS, 'load_shape'),
    columns = {
        'utility': 'string',
        'quarter': 'int',
        'month': 'int',
        'hour_of_year': 'int',
        'hour_of_day': 'int',
        'load_shape': 'string',
        'value': 'float'
    }
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return unpivot(
        context.fetchdf(f"SELECT * FROM {context.resolve_table('california.ca_hourly_electric_load_shapes_horizontal')}")
    )


def unpivot(df: DataFrame) -> DataFrame:
    """
    Unpivot the elec_load_shape table to have a row for each load shape name and value.
    """
    if 'region' in df.columns:  # drop the always null region column
        df = df.drop(columns=['region'])
    unpivoted_df = df.melt(
            id_vars=ID_COLUMNS,
            value_vars=[col for col in df.columns if col not in ID_COLUMNS],
            var_name='load_shape',
            value_name='value'
    )

    unpivoted_df['load_shape'] = unpivoted_df['load_shape'].str.upper()

    return unpivoted_df
