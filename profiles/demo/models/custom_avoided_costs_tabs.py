from typing import Any

from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd

ID_COLUMNS = ['commodity', 'avoided_cost', 'utility', 'year', 'month', 'hour_of_year', 'hour_of_day']

@model(
    name='openbca_input.custom_avoided_costs_tabs',
    kind='FULL',
    grain=ID_COLUMNS,
    columns = {
        'commodity': 'string',
        'avoided_cost': 'string',
        'avoided_cost_subset': 'string',
        'year': 'int',
        'quarter': 'int',
        'month': 'int',
        'hour_of_day': 'int',
        'hour_of_year': 'int',
        'value': 'float',
        'sheet_name': 'string'
    }
)
def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    return pd.concat([
            load_avoided_costs_excel_file('ELECTRICITY', 'custom_electric_avoided_costs_tabs.xlsx'),
            load_avoided_costs_excel_file('GAS', 'custom_gas_avoided_costs_tabs.xlsx'),
        ])


def load_avoided_costs_excel_file(commodity: str, input_file: str) -> DataFrame:
    sheets_dict = pd.read_excel(pd.ExcelFile(f"profiles/demo/data/{input_file}"), sheet_name=None)
    return (
        pd.concat([df.assign(sheet_name=sheet) for sheet, df in sheets_dict.items()], ignore_index=True)
        .assign(commodity=commodity)
        .assign(quarter=lambda x: (x['month'] - 1) // 3 + 1)
    )
