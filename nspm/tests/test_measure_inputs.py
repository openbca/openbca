from nspm.models.raw import measure_inputs
from nspm.models.raw.measure_inputs import MEASURE_INPUTS_COLUMNS

def test_measure_inputs_columns_match_decorator():
    df = measure_inputs.measure_inputs_model()

    expected_columns = set(MEASURE_INPUTS_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) == 2

    assert df["measure_id"].notna().all(), "measure_id should not contain null values"

