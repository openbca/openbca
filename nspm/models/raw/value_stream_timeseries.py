from sqlmesh import model
import pandas as pd

VALUE_STREAM_TS_COLUMNS = {
    "value_stream": "string",
}


@model(
    name="nspm_raw.value_stream_timeseries",
    kind="FULL",
    columns=VALUE_STREAM_TS_COLUMNS
)
def value_stream_ts_model() -> pd.DataFrame:
    xls = pd.ExcelFile('nspm/input/OpenBCA Code PROGRAM File.xlsx', engine='openpyxl')
    sheets_to_load = xls.sheet_names[3:]

    all_dfs = []
    for sheet in sheets_to_load:
        df = pd.read_excel(xls, sheet_name=sheet)
        source_name = sheet.replace(" - Input", "")
        df["source"] = source_name
        all_dfs.append(df)

    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Display or use the combined DataFrame
    print(combined_df.head())

    return df
