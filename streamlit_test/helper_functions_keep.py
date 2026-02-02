import numpy as np
import pandas as pd

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
    base_unit_label = ''
    unit_labels = []

    rescale = False
    dollar_magnitude = 0
    for col in [x_col, y_col]:
        if col is not None:
            max_val = max(abs(df[col].max()), abs(df[col].min()))
            if max_val > 0.0 and max_val <= 0.01:
                num_decimals = len(str(max_val).split('.')[1]) if '.' in str(max_val) else int(str(max_val).split('-')[1].replace('0', ''))
                df[col+'_original'] = df[col]
                df[col] = df[col].apply(lambda x: x*10**(num_decimals))
                unit_labels.append(f"(${num_decimals})")
            else:
                dollar_magnitude = np.floor(len(str(np.floor(max(abs(df[col].max()), abs(df[col].min()))))) / 3) - 1
                dollar_magnitude = max(0, dollar_magnitude)
                rescale = True
        # else:
        #     unit_labels.append('')
        
    for col in [x_col, y_col]:
        if rescale:
            if col is not None:
                df[col+'_original'] = df[col]
                df[col] = df[col].apply(lambda x: x/10**(dollar_magnitude * 3) if dollar_magnitude > 0 else x)
                base_unit_label = dollar_magnitude_dict[dollar_magnitude]
                unit_labels.append(f"(${base_unit_label})")
            else:
                unit_labels.append('')
    print("rescale = ", rescale)

    if return_scale_exponent:
        scale_exponent = dollar_magnitude_dict_reverse[base_unit_label] * 3 if rescale else 0
        return df, unit_labels, scale_exponent
    else:
        return df, unit_labels
