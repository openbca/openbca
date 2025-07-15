from nspm.models.raw import value_stream_timeseries
from nspm.models.raw.value_stream_timeseries import VALUE_STREAM_TS_COLUMNS


def test_value_stream_timeseries_columns_match_decorator():
    df = value_stream_timeseries.value_stream_ts_model()

    expected_columns = set(VALUE_STREAM_TS_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) > 1000

    assert df["value"].notna().all()

    assert df.duplicated(subset=["value_stream", "year", "month", "hour"]).sum() == 0
