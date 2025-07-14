

from nspm.models import loadshape_mapping
from nspm.models.loadshape_mapping import LOAD_SHAPE_MAPPING_COLUMNS


def test_loadshape_mapping_columns_match_decorator():
    df = loadshape_mapping.loadshape_mapping_hourly_model()

    expected_columns = set(LOAD_SHAPE_MAPPING_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) == 4

    assert df["program_id"].notna().all(), "program_id should not contain null values"

