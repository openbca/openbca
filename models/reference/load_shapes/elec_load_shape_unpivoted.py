from typing import Any

from sqlmesh import model, ExecutionContext
import pandas as pd

ID_COLUMNS = ['state', 'utility', 'region', 'quarter', 'month', 'hour_of_year', 'hour_of_day']

@model(
    name='flexvalue_reference.elec_load_shape_unpivoted',
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
    df = pd.read_csv('test_data/test_real_data_calculations_aggregated/ca_hourly_electric_load_shapes_horizontal_copy.csv')

    return df.melt(
        id_vars=ID_COLUMNS,
        value_vars=[col for col in df.columns if col not in ID_COLUMNS],
        var_name='load_shape_name',
        value_name='value'
    )
