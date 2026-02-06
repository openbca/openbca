import streamlit as st 
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import duckdb
from validation_functions import (
    validate_required_parameters, 
    validate_unique_ids, 
    validate_load_shapes, 
    validate_avoided_cost_load_shape_granularity
)

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

st.markdown("## Welcome to the OpenBCA")
st.markdown("###### The OpenBCA software executes Jurisdiction Specific Tests developed under National Standard Practice Manual guidance.")

# Resolve paths relative to this file, not the current working directory.
REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_TEMPLATES_DIR = REPO_ROOT / "nspm" / "input_templates"
OUTPUT_DIR = REPO_ROOT / "output"
INPUT_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

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

                with duckdb.connect(str(validation_db_path)) as con:

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

    # Show download button if database exists and model has been run
    with col2:
        try:
            with duckdb.connect(str(db_path), read_only=True) as con:
                # Query the data and convert to CSV string
                summary_results_df = con.execute(
                    "SELECT * FROM openbca.core_layer3_finalization.results_summary_by_id"
                ).df()
                summary_results_csv = summary_results_df.to_csv(index=False)
                
                download_summary_results = st.button("Download Summary Results", type="secondary")
                if download_summary_results:
                    # Save file to OUTPUT_DIR
                    output_file_path = OUTPUT_DIR / "results_summary_by_id.csv"
                    # DD: Write directly to the output file path, avoids windows carriage return issues when writing from a string buffer
                    summary_results_df.to_csv(output_file_path, index=False)
                    st.success(f"Summary results saved to {output_file_path}")

        except Exception as e:
            # If there's an error (e.g., table doesn't exist yet), just skip showing the button
            pass

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
    
    # Display persistent status messages
    with col2:
        if st.session_state.model_run_status == "success":
            st.success("OpenBCA model completed successfully.")
            st.page_link("pages/Insights_and_Analysis.py", label="Go to **Insights and Analysis**", icon="🔍")

        elif st.session_state.model_run_status == "error" and st.session_state.model_run_error:
            st.error(st.session_state.model_run_error)