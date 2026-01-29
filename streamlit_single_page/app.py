import streamlit as st 
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import duckdb
import pandas as pd
import numpy as np
import time
from validation_functions import (
    validate_required_parameters, 
    validate_unique_ids, 
    validate_load_shapes, 
    validate_avoided_cost_load_shape_granularity
)
from figures import waterfall_multitier_fig, hour_of_day_ls_fig, bar_fig

st.set_page_config(layout="wide")

col1, col2, col3, col4, col5 = st.columns(5)

LOGOS_DIR = Path(__file__).resolve().parent / "logos"
with col1:
    logo_col, _spacer_col = st.columns([2, 1])
    with logo_col:
        st.image(str(LOGOS_DIR / "NASEO.jpg"), width='stretch')
with col2:
    _spacer_col = st.columns([1, 1])
with col3:
    logo_col, _spacer_col = st.columns([1, 1])
    with logo_col:
        st.image(str(LOGOS_DIR / "ICF.jpg"), width='stretch')
with col4:
    _spacer_col = st.columns([1, 1])
with col5:
    st.image(str(LOGOS_DIR / "RECURVE.jpg"), width='stretch')

# Resolve paths relative to this file, not the current working directory.
REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_TEMPLATES_DIR = REPO_ROOT / "nspm" / "input_templates"
OUTPUT_DIR = REPO_ROOT / "output"
#INPUT_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Match Makefile defaults (DB?=output/openbca.db, DBV?=output/openbca_input_validation.db) if not set.
DEFAULT_OUTPUT_DB = REPO_ROOT / "output" / "openbca.db"
DEFAULT_OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)
DEFAULT_VALIDATION_DB = REPO_ROOT / "output" / "openbca_input_validation.db"
DEFAULT_VALIDATION_DB.parent.mkdir(parents=True, exist_ok=True)

program_input_file_name = "OpenBCA Program Input.xlsx"
configuration_file_name = "OpenBCA Configuration.xlsm"

# Check if input files and output database already exist in the input templates directory.
program_input_file_path = INPUT_TEMPLATES_DIR / program_input_file_name
configuration_file_path = INPUT_TEMPLATES_DIR / configuration_file_name
if 'input_files_exist_initial' not in st.session_state:
    st.session_state.input_files_exist_initial = program_input_file_path.exists() and configuration_file_path.exists()

if 'output_db_exists_initial' not in st.session_state:
    st.session_state.output_db_exists_initial = DEFAULT_OUTPUT_DB.exists()

if st.session_state.input_files_exist_initial:
    st.info("Input files are already detected. You can upload new files if desired or skip to validation of the existing files.")

if st.session_state.output_db_exists_initial:
    st.info("An OpenBCA output database already exists. You can rerun OpenBCA with new inputs or skip to the Insights and Analysis section.")

if 'display_file_overwrite_warning' not in st.session_state:
    st.session_state.display_file_overwrite_warning = True if st.session_state.input_files_exist_initial else False

def set_file_overwrite_warning_true():
    st.session_state.display_file_overwrite_warning = True

col1, col2 = st.columns(spec=[0.35, 0.65], gap="medium", border=False)

with col1:

    with st.form("Upload Input Files", clear_on_submit=True, border=False):
        st.markdown("##### Upload Input Files")
        uploaded_files = st.file_uploader(
            "Upload Program Input and Configuration files:",
            accept_multiple_files=True, 
            type=['xlsm', 'xlsx'], 
            help=f"Upload {program_input_file_name} and {configuration_file_name} files. Multiple files can be uploaded at once.",
            key='file_uploader'
            )

        if st.session_state.display_file_overwrite_warning:
            st.warning("New uploads will overwrite existing files.", icon="⚠️")

        file_submitted = st.form_submit_button("Upload selected files", on_click=set_file_overwrite_warning_true)
        
        if file_submitted and uploaded_files is not None:
            for uploaded_file in uploaded_files:
                file_name = Path(uploaded_file.name).name
                file_path = INPUT_TEMPLATES_DIR / file_name
                with file_path.open("wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved: `{file_name}`")

with col2:
    with st.container(border=False):
        st.markdown("##### Run Validations")

        validation_db_value = os.environ.get("DBV", str(DEFAULT_VALIDATION_DB))
        st.write(f"Using Database: `{validation_db_value.replace(str(REPO_ROOT), '').lstrip('/')}`")

        validation_db_path = Path(validation_db_value).expanduser()
        validation_db_exists_initial = validation_db_path.exists()

        validate_button = st.button("Validate Input Files", type="primary")
        if validate_button:
            if not (program_input_file_path.exists() and configuration_file_path.exists()):
                st.error("Input files not found. Please upload input files.")

            else:
                if validation_db_exists_initial:
                    validation_db_path.unlink()

                cmd = ["make", "run-input-transform-validations"]
                env = os.environ.copy()
                # Set DBV to the validation database path (Makefile will use DB=$(DBV))
                env["DBV"] = str(validation_db_path)

                with st.spinner("Running input parsing and validations... this can take a bit.", show_time=True):
                    try:
                        result = subprocess.run(
                            cmd,
                            cwd=str(REPO_ROOT),
                            env=env,
                            capture_output=True,
                            text=True,
                        )
                    except FileNotFoundError as e:
                        st.error(f"Failed to run command: {e}")
                    
                    else:
                        if result.returncode == 0:
                            pass
                        else:
                            st.error(f"Validations failed (exit code {result.returncode}).")

                con = duckdb.connect(str(validation_db_path))

                ## Required Parameters Validations
                required_parameters_query = "SELECT * FROM core_validations.required_parameters_v"    
                required_parameters_df = con.execute(required_parameters_query).df()
                global_parameters_query = "SELECT * FROM core_validations.global_parameters_v"    
                global_parameters_df = con.execute(global_parameters_query).df()
                unique_ids_query = "SELECT * FROM core_validations.unique_ids_v"    
                unique_ids_df = con.execute(unique_ids_query).df()
                load_shapes_query = "SELECT * FROM core_validations.load_shape_v"    
                load_shapes_df = con.execute(load_shapes_query).df()
                avoided_cost_load_shape_granularity_query = "SELECT * FROM core_validations.avoided_cost_load_shape_granularity_v"    
                avoided_cost_load_shape_granularity_df = con.execute(avoided_cost_load_shape_granularity_query).df()

                validate_required_parameters(required_parameters_df, "Program Inputs", "Row-level parameters")
                validate_required_parameters(global_parameters_df, "Configuration", "Global parameters")
                validate_unique_ids(unique_ids_df, program_input_file_name, "Unique IDs")
                validate_load_shapes(load_shapes_df, program_input_file_name, "Load Shape")
                validate_avoided_cost_load_shape_granularity(avoided_cost_load_shape_granularity_df, program_input_file_name, "Agreement between avoided cost and load shape granularity")

st.divider()
st.subheader("Run OpenBCA Model")

db_value = os.environ.get("DB", str(DEFAULT_OUTPUT_DB))
db_path = Path(db_value).expanduser()
db_exists = db_path.exists()

col1, col2 = st.columns(spec=[0.35, 0.65], gap="small", border=False)
db_handling = "Overwrite existing output database"
if db_exists:
    db_handling = col1.radio(
        "How would you like to handle the existing output database?",
        [
            "Keep existing output database (do not run OpenBCA)",
            "Backup existing output database, then run OpenBCA",
            "Overwrite existing output database"
        ],
        index=0,
    )

backup_name = None
if db_handling.startswith("Backup"):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    default_backup = db_path.with_name(f"{db_path.stem}.{ts}.bak{db_path.suffix}")
    backup_name = col1.text_input(
        "Backup database filename:",
        value=str(default_backup),
        help="Example: output/openbca.20260119-153000.bak.db",
    )

if db_handling in ["Overwrite existing output database", "Backup existing output database, then run OpenBCA"]:
    # Initialize session state for model run status
    if 'model_run_status' not in st.session_state:
        st.session_state.model_run_status = None
    if 'model_run_error' not in st.session_state:
        st.session_state.model_run_error = None
    
    run_clicked = col1.button("Run OpenBCA", type="primary")
    if run_clicked:
        # Clear previous status when starting a new run
        st.session_state.model_run_status = None
        st.session_state.model_run_error = None
        col2.write("Initiating OpenBCA model run...")

        # Handle backup before running SQLmesh
        if db_exists:
            if db_handling == "Backup existing output database, then run OpenBCA":
                # Use the user-provided backup filename
                if backup_name:
                    backup_path = Path(backup_name).expanduser()
                    # Ensure the backup path is in the output folder if it's a relative path
                    if not backup_path.is_absolute():
                        backup_path = db_path.parent / backup_path.name
                    
                    try:
                        shutil.copy2(db_path, backup_path)
                        st.info(f"Backed up existing database to: {backup_path}")
                        db_path.unlink()
                    except Exception as e:
                        st.error(f"Failed to create backup or unlink existing database: {e}")
                        st.stop()
                else:
                    st.error("Backup filename is required.")
                    st.stop()
            
            elif db_handling == "Overwrite existing output database":
                # Create an auto-generated backup before overwriting
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_path = db_path.with_name(f"{db_path.stem}.{ts}.bak{db_path.suffix}")
                
                try:
                    # shutil.copy2(db_path, backup_path)
                    # st.info(f"Backed up existing database to: {backup_path}")
                    # Remove the original file to ensure SQLmesh runs from end to end
                    db_path.unlink()
                    #st.info(f"Removed original database: {db_path}")
                except Exception as e:
                    st.error(f"Failed to backup and remove existing database: {e}")
                    st.stop()

        cmd = ["uv", "run", "sqlmesh", "-p", "nspm", "-p", "core", "plan", "--auto-apply"]
        env = os.environ.copy()
        env["DB"] = str(db_path)

        with col2:
            with st.spinner("Running OpenBCA Model... this can take a bit.", show_time=True):
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=str(REPO_ROOT),
                        env=env,
                        capture_output=True,
                        text=True,
                    )
                except FileNotFoundError as e:
                    st.session_state.model_run_status = "error"
                    st.session_state.model_run_error = f"Failed to run command: {e}"
                
                else:
                    if result.returncode == 0:
                        st.session_state.model_run_status = "success"
                        st.session_state.model_run_error = None
                        st.balloons()
                    else:
                        st.session_state.model_run_status = "error"
                        st.session_state.model_run_error = f"Model failed (exit code {result.returncode})."

            # if result.stdout.strip():
            #     st.text_area("stdout", result.stdout, height=240)
            # if result.stderr.strip():
            #     st.text_area("stderr", result.stderr, height=240)
    
    # Display persistent status messages
    with col2:
        if st.session_state.model_run_status == "success":
            st.success("OpenBCA model completed successfully.")
        elif st.session_state.model_run_status == "error" and st.session_state.model_run_error:
            st.error(st.session_state.model_run_error)
    
    # Show download button if database exists and model has been run
    if db_path.exists():
        with col2:
            try:
                con = duckdb.connect(str(db_path), read_only=True)
                # Query the data and convert to CSV string
                summary_results_df = con.execute(
                    "SELECT * FROM openbca.core_layer3_finalization.results_summary_by_id"
                ).df()
                summary_results_csv = summary_results_df.to_csv(index=False)
                
                download_summary_results = st.button("Download Summary Results", type="secondary")
                if download_summary_results:
                    # Save file to OUTPUT_DIR
                    #OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                    output_file_path = OUTPUT_DIR / "results_summary_by_id.csv"
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(summary_results_csv)
                    st.success(f"Summary results saved to {output_file_path}")
                con.close()
            except Exception as e:
                # If there's an error (e.g., table doesn't exist yet), just skip showing the button
                pass

st.divider()
st.subheader("OpenBCA Insights and Analysis")
st.write(f"Using Database: `{db_value}`")
db_exists_now = db_path.exists()

if db_exists_now:
    con = duckdb.connect(str(db_path), read_only=True)

    st.sidebar.title("Filter Results")

    jst_query = "SELECT * FROM openbca.core_layer3_finalization.jst_ratio"

    jst_results_df = con.execute(jst_query).df()

    jst_ratio = jst_results_df['jst_ratio'].values[0]
    total_costs = -jst_results_df['total_costs'].values[0]
    total_benefits = jst_results_df['total_benefits'].values[0]
    net_benefits = jst_results_df['net_benefits'].values[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Benefits", value=f"${total_benefits:,.0f}")
    col2.metric(label="Total Costs", value=f"${total_costs:,.0f}")
    col3.metric(label="Net Benefits", value=f"${net_benefits:,.0f}")
    col4.metric(label="JST Ratio", value=f"{jst_ratio:.2f}")

    measure_filters_query = f"""
    SELECT  
    id
    , program_name 
    , measure_name
    , label_1
    , label_2
    , label_3
    , label_4
    , label_5
    FROM 
    openbca.core_layer0_base.measures
    """

    measure_filters_df = con.execute(measure_filters_query).df()
    
    filter_options = []
    for col in measure_filters_df.columns:
        if len(measure_filters_df[col].unique()) > 1:
            filter_options.append(col)
    
    filters_dict = {}
    for i, option in enumerate(filter_options): 
        options = measure_filters_df[option].unique().tolist()
        filters_dict[option] = st.sidebar.multiselect(
            label = f"Limit {' '.join(option.split('_')).title()} to:".replace(" Id ", " ID "),
            options = options,
            key = f"filter_{option}",
        )

        if len(filters_dict[option]) == 0:
            filters_dict[option] = options
    
    where_sql = f"WHERE 1=1"
    for option, values in filters_dict.items():
        where_snippet = ', '.join(["'{}'".format(value) for value in values])
        where_sql += f" AND m.{option} IN ({where_snippet})"
    
    aggregation_options = ["Commodity", "Value Stream"]
    
    col1, col2 = st.columns(spec=[0.5, 0.5], gap="medium", border=False)

    with col1:
        aggregation_filter = st.radio(
            label = "Breakout results by:", 
            options = aggregation_options, 
            horizontal = True,
            index = 0, 
            )

        aggregation_column = aggregation_filter.lower().replace(" ", "_")
            
        aggregation_query = f"""
        SELECT 
        {aggregation_column} 
        , sum(final_dollar_value) as final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        GROUP BY 
        {aggregation_column} 
        """

        #st.write(aggregation_query)

        aggregation_results_df = con.execute(aggregation_query).df().query("final_dollar_value != 0")
        aggregation_results_total_df = pd.DataFrame([['total', aggregation_results_df['final_dollar_value'].sum()]], columns=[aggregation_column, 'final_dollar_value'])
        aggregation_results_df = pd.concat([aggregation_results_df, aggregation_results_total_df])
        aggregation_results_df['total'] = aggregation_results_df[aggregation_column].apply(lambda x: True if x == 'total' else False)

        max_val_len = len(str(int(max(abs(aggregation_results_df['final_dollar_value'].max()), abs(aggregation_results_df['final_dollar_value'].min())))))
        dollar_magnitude = np.floor(max_val_len / 3)
        dollar_magnitude_dict = {0:'', 1:'K', 2:'M', 3:'B', 4:'T'}
        num_bars = len(aggregation_results_df)

        def determine_label_sig_figs(num_bars: int) -> int:
            if num_bars <= 10:
                return 3
            elif num_bars <= 15:
                return 2
            elif num_bars <= 20:
                return 1
            else:
                return 0
        
        num_bars_sig_figs = determine_label_sig_figs(num_bars)
        
        aggregation_results_df['final_dollar_value_label'] = aggregation_results_df['final_dollar_value'].apply(lambda x: x/10**(dollar_magnitude * 3) if dollar_magnitude > 0 else x)
        #st.dataframe(aggregation_results_df, width='stretch', hide_index=True)

        waterfall_fig = waterfall_multitier_fig(
            df = aggregation_results_df,
            col = 'final_dollar_value_label',
            category = aggregation_column,
            tiers = None,
            sorting_list = ['total', 'final_dollar_value'],
            sort_directions = [True, False],
            figsize = (11, 6),
            include_line = False,
            include_value_labels = True,
            value_labels_decimals = num_bars_sig_figs,
            title = "Benefit and Cost Breakdown",
            annotations = [None],
            ylabel = f'Dollars (${dollar_magnitude_dict[dollar_magnitude]})',
            ylims = None,
        )
        
        col1.pyplot(waterfall_fig, clear_figure=True)
    
    with col2:
        benefits_commodity_options = con.execute("""
            SELECT 
            DISTINCT commodity 
            FROM 
            openbca.core_layer3_finalization.final_value_calculations_ts
            WHERE
            commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
            ORDER BY 
            commodity
            """
            ).df()['commodity'].tolist()

        commodity_filter = st.radio(
            label = "Select Commodity:", 
            options = benefits_commodity_options, 
            horizontal = True,
            index = 0 if 'ELECTRIC' not in benefits_commodity_options else benefits_commodity_options.index('ELECTRIC'), 
            )
        
        temporal_cols = ['hour_of_day', 'month', 'year']

        populated_temporal_cols = []
        for col in temporal_cols:
            if len(
                con.execute(
                    f"""
                    SELECT 
                    commodity 
                    FROM 
                    openbca.core_layer3_finalization.final_value_calculations_ts 
                    WHERE 
                    commodity = '{commodity_filter}'
                    AND {col} IS NOT NULL
                    LIMIT 1
                    """
                    ).df()
                ) > 0:
                populated_temporal_cols.append(col)
        
        temporal_aggregation_filter = st.radio(
            label = "Aggregate results by:",
            options = [' '.join(col.split('_')).title().replace("Of", "of") for col in populated_temporal_cols],
            index = 0,
            horizontal = True,
            )

        temporal_aggregation_filter = temporal_aggregation_filter.lower().replace(" ", "_")

        temporal_aggregation_query = f"""
        WITH benefits AS (
        SELECT 
        {temporal_aggregation_filter}
        , sum(final_dollar_value) as final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        GROUP BY 
        {temporal_aggregation_filter}
        )
        , savings AS (
        SELECT 
        {temporal_aggregation_filter}
        , sum(total_net_annual_energy_savings) as total_net_annual_energy_savings
        FROM 
        openbca.core_layer3_finalization.final_savings_calculations_ts fsc
        JOIN openbca.core_layer0_base.measures m ON 
        fsc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        GROUP BY 
        {temporal_aggregation_filter}
        )
        SELECT 
        b.*
        , s.total_net_annual_energy_savings as net_annual_savings
        FROM 
        benefits b 
        JOIN savings s ON 
        b.{temporal_aggregation_filter} = s.{temporal_aggregation_filter}
        ORDER BY
        b.{temporal_aggregation_filter}
        """

        #st.write(temporal_aggregation_query)

        temporal_aggregation_results_df = con.execute(temporal_aggregation_query).df()
        #st.dataframe(temporal_aggregation_results_df, width='stretch', hide_index=True)

        temporal_aggregation_bar_fig = bar_fig(
        df = temporal_aggregation_results_df,
        col = 'final_dollar_value',
        category = temporal_aggregation_filter,
        groupings = None,
        uncertainty_col = None,
        figsize= (10, 6),
        y2_col = 'net_annual_savings',
        min_y2_counts = 0,
        pin_yaxis_zeros = True,
        single_bar_color="dimgray",
        horizontal = False,
        space_fraction = 0.65,
        sort_by = None,
        sort_ascending = True,
        title = None,
        xlabel = None,
        ylabel = '$ Benefits',
        y2label = 'Savings',
        ax = None,
        legend = True,
        legend_loc = None,
        label_map = None
        )

        st.pyplot(temporal_aggregation_bar_fig, clear_figure=True)


    # hod_fig = hour_of_day_ls_fig(
    #     df = temporal_aggregation_results_df,
    #     cols_dict = {'final_dollar_value': {'label': 'Final Dollar Value'}},
    #     peak_period = [-1],
    #     figsize = (10, 6),
    #     title = 'Benefits Load Profile',
    #     ylims = None,
    #     ylabel = '$',
    #     legend_loc = 'upper left',
    # )

    # st.pyplot(hod_fig, clear_figure=True)
    con.close()
else:
    st.info("OpenBCA outputs not found. Run the OpenBCA model to generate results.")

