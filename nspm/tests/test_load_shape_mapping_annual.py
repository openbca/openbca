from nspm.models.parsing import loadshape_mapping_annual
from nspm.models.parsing.loadshape_mapping_annual import LOAD_SHAPE_MAPPING_ANNUAL_COLUMNS


def test_loadshape_mapping_annual_columns_match_decorator():
    df = loadshape_mapping_annual.loadshape_mapping_annual_model()

    expected_columns = set(LOAD_SHAPE_MAPPING_ANNUAL_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) == 10

    assert df["load_shape_name"].notna().all()
    assert df["year_ref"].notna().all()
    assert df["load_shape_normalized_fraction"].notna().all()
