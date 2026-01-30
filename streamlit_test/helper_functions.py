import numpy as np
import pandas as pd

def determine_label_sig_figs(num_bars: int) -> int:
    if num_bars <= 10:
        return 3
    elif num_bars <= 15:
        return 2
    elif num_bars <= 20:
        return 1
    else:
        return 0

def determine_dollar_magnitude(df:pd.DataFrame, x_col: str = None, y_col: str = None) -> tuple[pd.DataFrame, list[str]]:
    
    dollar_magnitude_dict = {0:'', 1:'k', 2:'M', 3:'B', 4:'T'}
    unit_labels = []

    for col in [x_col, y_col]:
        if col is not None:
            max_val = max(abs(df[col].max()), abs(df[col].min()))
            if max_val > 0.0 and max_val <= 0.01:
                num_decimals = len(str(max_val).split('.')[1]) if '.' in str(max_val) else int(str(max_val).split('-')[1].replace('0', ''))
                df[col+'_original'] = df[col]
                df[col] = df[col].apply(lambda x: x*10**(num_decimals))
                unit_labels.append(f"(${num_decimals})")
            else:
                dollar_magnitude = np.floor(len(str(int(max(abs(df[col].max()), abs(df[col].min()))))) / 3)
                df[col+'_original'] = df[col]
                df[col] = df[col].apply(lambda x: x/10**(dollar_magnitude * 3) if dollar_magnitude > 0 else x)
                unit_labels.append(f"(${dollar_magnitude_dict[dollar_magnitude]})")
        
        else:
            unit_labels.append('')

    return df, unit_labels
