from pandas import DataFrame
from sqlmesh import model
import pandas as pd

VALUE_STREAM_TS_COLUMNS = {
    'value_stream': 'string',
    'year': 'int',
    'month': 'int',
    'hour': 'int',
    'value': 'float'
}


@model(
    name="nspm_raw.value_stream_timeseries",
    kind="FULL",
    columns=VALUE_STREAM_TS_COLUMNS
)
def value_stream_ts_model(*args, **kwargs) -> pd.DataFrame:
    xls = pd.ExcelFile('nspm/input/OpenBCA Code INPUT File.xlsx', engine='openpyxl')
    sheets_to_load = [sheet for sheet in xls.sheet_names if sheet.endswith('- Input')]

    all_dfs = []
    for sheet in sheets_to_load:
        df = pd.read_excel(xls, sheet_name=sheet)

        # get all column index of a new time_granularity table
        time_granularity_delimeters = [0, *[ i for i,c in enumerate(df.columns) if df.iloc[:, i].isnull().all()]]

        for i, time_granularity_delimeter in enumerate(time_granularity_delimeters):
            next_time_granularity_delimeter = time_granularity_delimeters[i+1] if i < (len(time_granularity_delimeters)-1) else (len(df.columns) )

            time_granularity_df = load_value_streams_time_granularity(df, time_granularity_delimeter, next_time_granularity_delimeter)

            if time_granularity_df is not None:
                time_granularity_df["value_stream"] = sheet.replace(" - Input", "")
                all_dfs.append(time_granularity_df)

    combined_df = pd.concat(all_dfs, ignore_index=True)

    return (
        combined_df
        .rename(columns={
            'value_stream' : 'value_stream',
            'Year': 'year',
            'Month': 'month',
            'Hour': 'hour',
            'value': 'value'
        }))


def load_value_streams_time_granularity(input_df: DataFrame, col_start: int, col_end: int) -> DataFrame | None:
    df = input_df[input_df.columns[col_start:col_end]]
    # get the real header
    columns = [(c if not str(c) == 'nan' else 'NA') for c in list(df.iloc[2])]
    df = df.iloc[3:]
    df.columns = columns

    non_numeric_cols = [c for c in df.columns if isinstance(c, str)]

    if len(columns) != len(non_numeric_cols) and 'Year' not in columns:  # FIXME some value_stream are Year * Year, skip them for now
        # pivot years columns into rows
        df = df.melt(
            id_vars=non_numeric_cols,
            var_name="Year",
            value_name="value",
        ).reset_index(drop=True)
        # filter out empty years
        df = df[df['Year'].notna()]
    else:
        # rename last column to value
        df = df.rename(columns={df.columns[-1]: 'value'})

    if df.iloc[:, -1].notnull().any():
        # drop empty columns
        df = df.dropna(axis=1, how='all')
        df = df[df['value'].notna()]
        # check df[value] is numeric
        if not pd.to_numeric(df['value'], errors='coerce').notna().all():
            return None
        return df.reindex(columns=['value_stream', 'Year', 'Month', 'Hour', 'value'])
    else:
        return None
