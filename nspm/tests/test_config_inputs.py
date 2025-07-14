from nspm.models.parsing import config_inputs
from nspm.models.parsing.config_inputs import CONFIG_INPUT_COLUMNS


def test_config_inputs_columns_match_decorator():
    df = config_inputs.config_inputs_model()

    expected_columns = set(CONFIG_INPUT_COLUMNS.keys())
    actual_columns = set(df.columns)
    assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"

    assert len(df) == 1
