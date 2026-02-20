import numpy as np
import pandas as pd
from itertools import product


def space_and_title(text: str) -> str:
    return ' '.join(str(text).split('_')).title().replace(
        "Commodity", "Impact Category").replace(
        " Id", " ID").replace(
        "Of", "of").replace(
        "Hvac", "HVAC").replace(
        "Ac ", "AC ").replace(
        "Nei", "NEI").replace(
        "Ghg", "GHG").replace(
        " (E)", "").replace(
        " (Ng)", "").replace(
        "Jst", "JST").replace(
        " Dollar Per Unit Year", '',).replace(
        " Dollar Per Unit", '').replace(
        " Dollar Per Year", '').replace(
        "Vs", "vs")


def reconstruct_column_name(text: str) -> str:
    return str(text).lower().replace(" ", "_").replace("impact_category", "commodity")


def determine_label_sig_figs(num_bars: int) -> int:
    if num_bars <= 8:
        return 3
    elif num_bars <= 10:
        return 2
    elif num_bars <= 18:
        return 1
    else:
        return 0

def determine_dollar_magnitude(df:pd.DataFrame, x_col: str = None, y_col: str = None, return_scale_exponent: bool = False) -> tuple[pd.DataFrame, list[str]]:
    
    dollar_magnitude_dict = {0:'', 1:'k', 2:'M', 3:'B', 4:'T'}
    dollar_magnitude_dict_reverse = {v: k for k, v in dollar_magnitude_dict.items()}
    unit_labels = []

    for col in [col for col in [x_col, y_col] if col is not None]:
        dollar_magnitude = np.floor(len(str(np.floor(max(abs(df[col].max()), abs(df[col].min()))))) / 3) - 1
        dollar_magnitude = max(0, dollar_magnitude)
        
    for col in [col for col in [x_col, y_col] if col is not None]:
        df[col+'_original'] = df[col]
        df[col] = df[col].apply(lambda x: x/10**(dollar_magnitude * 3) if dollar_magnitude > 0 else x)
        base_unit_label = dollar_magnitude_dict[dollar_magnitude]
        unit_labels.append(f" (${base_unit_label})")

    if return_scale_exponent:
        scale_exponent = dollar_magnitude_dict_reverse[base_unit_label] * 3 
        return df, unit_labels, scale_exponent
    else:
        return df, unit_labels

    
def determine_savings_magnitude(df:pd.DataFrame, x_col: str = None, y_col: str = None, unit: str = '') -> tuple[pd.DataFrame, list[str]]:
    
    savings_magnitude_dict = {0:'', 1:'k', 2:'M', 3:'B', 4:'T'}
    electric_savings_magnitude_dict = {0:'kWh', 1:'MWh', 2:'GWh', 3:'TWh'}
    unit_labels = []

    for col in [col for col in [x_col, y_col] if col is not None]:
        savings_magnitude = np.floor(len(str(np.floor(max(abs(df[col].max()), abs(df[col].min()))))) / 3) - 1
        savings_magnitude = max(0, savings_magnitude)
        
    for col in [col for col in [x_col, y_col] if col is not None]:
        df[col+'_original'] = df[col]
        df[col] = df[col].apply(lambda x: x/10**(savings_magnitude * 3) if savings_magnitude > 0 else x)
        if unit == '':
            unit_labels.append('' if savings_magnitude == 0 else f"({savings_magnitude_dict[savings_magnitude]})")
        elif unit == 'kWh':
            unit_labels.append(f"({electric_savings_magnitude_dict[savings_magnitude]})")
        else:
            unit_labels.append(f"({savings_magnitude_dict[savings_magnitude]}{unit})")

    return df, unit_labels


def generate_all_row_combinations_df(df: pd.DataFrame, col_1, col_2, numeric_cols = []) -> pd.DataFrame:
    if str(col_2.lower()) == 'none':
        return df

    else:
        # Full set of (col_1, col_2) pairs
        unique_col1 = df[col_1].unique()
        unique_col2 = df[col_2].unique()
        full_index = pd.DataFrame(
            product(unique_col1, unique_col2),
            columns=[col_1, col_2],
        )

        # One row per (col_1, col_2) in original data (if there can be duplicates)
        df_unique = df.drop_duplicates(subset=[col_1, col_2], keep="first")

        expanded_df = full_index.merge(df_unique[[col_1, col_2] + numeric_cols], on=[col_1, col_2], how="left")
        
        for col in numeric_cols:
            expanded_df[col] = expanded_df[col].fillna(0)

        return expanded_df