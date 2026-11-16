import streamlit as st
import pandas as pd
import time

def validate_required_parameters(df: pd.DataFrame, source_file: str, validation_name: str = 'Required parameters') -> list[str]:
    num_validations = len(df.columns)
    progress_bar_placeholder = st.empty()
    validation_results_placeholder = st.empty()
    time.sleep(1)
    
    validations_failed = []
    with validation_results_placeholder.container():
        for i, col in enumerate(df.columns):
            if df[col].values[0] == 0:
                st.markdown(f"✅ **{' '.join(col.split('_')[2:])}**: data complete")
            else:
                validations_failed.append(' '.join(col.split('_')[2:]))
                st.markdown(f"❌ **{' '.join(col.split('_')[2:])}**: data incomplete. Please check {source_file}.")

            progress_bar_placeholder.progress((i+1)/num_validations, f"Scanning {' '.join(col.split('_')[2:])}")
            time.sleep(1)

    if len(validations_failed) == 0:
        validation_results_placeholder.markdown(f"✅ {validation_name} data complete!")
    else:
        validation_results_placeholder.markdown(f"❌ {validation_name} data incomplete. Please check {', '.join(validations_failed)} fields.")
    time.sleep(0.5)

    progress_bar_placeholder.empty()

    return validations_failed


def validate_unique_ids(df: pd.DataFrame, source_file: str, validation_name: str = 'Unique IDs'):
    validation_results_placeholder = st.empty()
    with st.spinner(f"Validating {validation_name}..."):
        time.sleep(2)
        if len(df) == 0:
            validation_results_placeholder.markdown(f"✅ {validation_name} verified!")
        else:
            validation_results_placeholder.markdown(f"❌ {validation_name} failed. The following duplicate IDs were found. Please ensure all IDs are unique and reupload {source_file}.")
            st.dataframe(df, hide_index=True, height="auto")


def validate_load_shapes(df: pd.DataFrame, source_file: str, validation_name: str = 'Load Shape'):
    validation_results_placeholder = st.empty()
    with st.spinner(f"Validating {validation_name}..."):
        time.sleep(2)
        if len(df) == 0:
            validation_results_placeholder.markdown(f"✅ {validation_name} mapping verified!")
        else:
            validation_results_placeholder.markdown(f"❌ {validation_name} mapping failed. The following load shapes were found in the measure inputs but not in the electric and/or natural gas load shapes. Please check {source_file} and ensure all load shapes are provided and mapped correctly.")
            st.dataframe(df, hide_index=True, height="auto")


def validate_avoided_cost_load_shape_granularity(df: pd.DataFrame, source_file: str, validation_name: str = 'Agreement between avoided cost and load shape granularity'):
    validation_results_placeholder = st.empty()
    with st.spinner(f"Validating {validation_name}..."):
        time.sleep(2)
        if len(df.query("validation_result == 'FAIL'")) == 0:
            validation_results_placeholder.markdown(f"✅ {validation_name} verified!")
        else:
            validation_results_placeholder.markdown(f"❌ {validation_name} failed. The following load shapes were found to have lower granularity than demanded by the avoided cost profile. Please check {source_file} and ensure all load shapes are at equal or higher granularity than the avoided cost profile.")
            st.dataframe(df.query("validation_result == 'FAIL'"), hide_index=True, height="auto")


def validate_load_shape_normalization(df: pd.DataFrame, source_file: str, validation_name: str = 'Load Shape Normalization'):
    validation_results_placeholder = st.empty()
    with st.spinner(f"Validating {validation_name}..."):
        time.sleep(2)
        if len(df.query("passed_normalization_test == 'FAIL'")) == 0:
            validation_results_placeholder.markdown(f"✅ {validation_name} verified!")
        else:
            validation_results_placeholder.markdown(f"⚠️ Warning: The following load shapes were found to fall outside expected normalization thresholds (0.999 - 1.001). Please check {source_file} and ensure all load shapes are properly catalogued in the Define Load Shape Names tab and normalized as intended.")
            st.dataframe(df.query("passed_normalization_test == 'FAIL'"), hide_index=True, height="auto")