from nspm.models.parsing import loadshape_mapping_hourly
from nspm.models.parsing.loadshape_mapping_hourly import LOAD_SHAPE_MAPPING_HOURLY_COLUMNS


def test_loadshape_mapping_hourly_columns_match_decorator():
    df = loadshape_mapping_hourly.loadshape_mapping_hourly_model()

    expected_columns = set(LOAD_SHAPE_MAPPING_HOURLY_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) == 10 * 8760

    assert df["load_shape_name"].notna().all()
    assert df["hour_of_year"].notna().all()
    assert df["load_shape_normalized_fraction"].notna().all()
