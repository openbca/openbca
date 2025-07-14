from nspm.models.parsing import program_inputs
from nspm.models.parsing.program_inputs import PROGRAM_INPUT_COLUMNS


def test_program_inputs_columns_match_decorator():
    df = program_inputs.program_inputs_model()

    expected_columns = set(PROGRAM_INPUT_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) == 4

    assert df["program_id"].notna().all(), "program_id should not contain null values"

