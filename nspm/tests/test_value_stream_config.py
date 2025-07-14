from nspm.models.raw import value_stream_config
from nspm.models.raw.value_stream_config import VALUE_STREAM_CONFIG_COLUMNS


def test_value_stream_config_columns_match_decorator():
    df = value_stream_config.value_stream_config_model()

    expected_columns = set(VALUE_STREAM_CONFIG_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) == 59
    assert df["value_stream"].notna().all()
    assert df["calculation_type "].notna().all()
