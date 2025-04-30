from typing import Any

from sqlmesh import model, ExecutionContext
import pandas as pd

ID_COLUMNS = ['state', 'utility', 'region', 'quarter', 'month', 'hour_of_year', 'hour_of_day']

@model(
    name='flexvalue.elec_load_shape_unpivoted',
    kind='FULL',
    grain=(*ID_COLUMNS, 'load_shape_name'),
    columns = {
        'state': 'string',
        'utility': 'string',
        'region': 'string',
        'quarter': 'int',
        'month': 'int',
        'hour_of_year': 'int',
        'hour_of_day': 'int',
        'load_shape_name': 'string',
        'value': 'float'
    }
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    """
    Unpivot the elec_load_shape table to have a row for each load shape name and value.
    """
    df = context.fetchdf(f"SELECT * FROM flexvalue_input.elec_load_shape")

    return df.melt(
        id_vars=ID_COLUMNS,
        value_vars=[col for col in df.columns if col not in ID_COLUMNS],
        var_name='load_shape_name',
        value_name='value'
    )
