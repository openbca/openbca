import streamlit as st 
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import duckdb
import pandas as pd
from figures import waterfall_multitier_fig

st.title("OpenBCA Input File Uploader and Application Launcher")

# Resolve paths relative to this file, not the current working directory.
REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_TEMPLATES_DIR = REPO_ROOT / "nspm" / "input_templates"
INPUT_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Match Makefile default (DB?=output/openbca.db) if not set.
DEFAULT_DB = REPO_ROOT / "output" / "openbca.db"
DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)

uploaded_files = st.file_uploader(
    "Upload Program Input and Configuration files:", accept_multiple_files=True, type=["xlsm", "xlsx"]
)

if uploaded_files:
    st.write("Review each file, then click **Save files**.")

    plan = []
    for uploaded_file in uploaded_files:
        file_name = Path(uploaded_file.name).name  # ensure it's just a filename
        file_path = INPUT_TEMPLATES_DIR / file_name

        exists = file_path.exists()
        if exists:
            action = st.radio(
                f"`{file_name}` already exists.",
                ["Keep existing", "Overwrite"],
                index=0,
                key=f"upload_action__{file_name}",
                horizontal=True,
            )
        else:
            st.caption(f"`{file_name}` will be saved to `nspm/input_templates`.")
            action = "Overwrite"  # treat as "save new file"

        plan.append((uploaded_file, file_name, file_path, action))

    if st.button("Save files", type="primary"):
        for uploaded_file, file_name, file_path, action in plan:
            if file_path.exists() and action == "Keep existing":
                st.info(f"Kept existing file: `{file_name}`")
                continue

            with file_path.open("wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Saved: `{file_name}`")

st.divider()
st.subheader("Run OpenBCA Model")

db_value = os.environ.get("DB", str(DEFAULT_DB))
st.write(f"Using DB: `{db_value}`")

db_path = Path(db_value).expanduser()
db_exists = db_path.exists()

db_handling = st.radio(
    "If the database file already exists, what should we do?",
    [
        "Overwrite existing OpenBCA output database",
        "Backup existing OpenBCA output database, then run OpenBCA",
        "Keep existing OpenBCA output database",
    ],
    index=2 if db_exists else 0,
)

backup_name = None
if db_handling.startswith("Backup"):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    default_backup = db_path.with_name(f"{db_path.stem}.{ts}.bak{db_path.suffix}")
    backup_name = st.text_input(
        "Backup filename (will be created next to the DB)",
        value=str(default_backup),
        help="Example: output/openbca.20260119-153000.bak.db",
    )

run_clicked = st.button("Run OpenBCA model", type="primary")
if run_clicked:
    if db_exists and db_handling.startswith("Keep"):
        st.warning("Stopped. Existing DB retained; model was not run.")
        st.stop()

    # Prepare DB according to selected handling option.
    try:
        if db_exists and db_handling.startswith("Overwrite"):
            db_path.unlink()
        elif db_exists and db_handling.startswith("Backup"):
            backup_path = Path(backup_name).expanduser() if backup_name else None
            if backup_path is None or backup_path == db_path:
                st.error("Invalid backup filename. Please choose a different name.")
                st.stop()
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(db_path), str(backup_path))
    except OSError as e:
        st.error(f"Failed to prepare DB file: {e}")
        st.stop()

    cmd = ["uv", "run", "sqlmesh", "-p", "nspm", "-p", "core", "plan", "--auto-apply"]
    env = os.environ.copy()
    env["DB"] = str(db_path)

    with st.spinner("Running OpenBCA Model... this can take a bit."):
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
                st.success("OpenBCA model completed successfully.")
            else:
                st.error(f"Model failed (exit code {result.returncode}).")

            # if result.stdout.strip():
            #     st.text_area("stdout", result.stdout, height=240)
            # if result.stderr.strip():
            #     st.text_area("stderr", result.stderr, height=240)

st.divider()
st.subheader("Explore BCA Results")

db_exists_now = db_path.exists()
if db_exists_now:
    con = duckdb.connect(str(db_path), read_only=True)

    jst_results_filter = st.multiselect(
        label = "Select results to display", 
        options = ["jst_ratio", "total_costs", "total_benefits", "net_benefits"], 
        default=["jst_ratio"], 
        )

    jst_query = f"SELECT {', '.join(jst_results_filter)} FROM openbca.core_layer3_finalization.jst_ratio"

    jst_results_df = con.execute(jst_query).df()
    
    st.dataframe(jst_results_df, use_container_width=True, hide_index=True)

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
    openbca.core_layer0_base.measures m
    """

    measure_filters_df = con.execute(measure_filters_query).df()
    aggregation_options = []
    for col in measure_filters_df.columns:
        if len(measure_filters_df[col].unique()) > 1:
            aggregation_options.append(col)

#st.radio(label, options, index=0, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, horizontal=False, captions=None, label_visibility="visible", width="content")
#st.checkbox(label, value=False, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible", width="content")

    id_sql = ''
    include_id_grouping_filter = False
    if 'id' in aggregation_options:
        include_id_grouping_filter = st.checkbox(
            label = "Include ID grouping",
            value = False,
            help = "Breakout results by id",
        )
        
        if include_id_grouping_filter:
            id_sql = 'fvc.id' 

        aggregation_options.remove('id')
    
    aggregation_filter = st.radio(
        label = "Select aggregation to display", 
        options = aggregation_options + ["commodity", "value_stream"], 
        horizontal = True,
        #default=["commodity"], 
        )

    aggregation_sql = aggregation_filter
    if id_sql != '': 
        aggregation_sql = aggregation_sql + ', ' + id_sql
        
    aggregation_query = f"""
    SELECT 
    {aggregation_sql} 
    , sum(final_dollar_value) as final_dollar_value
    FROM 
    openbca.core_layer3_finalization.final_value_calculations_ts fvc 
    JOIN openbca.core_layer0_base.measures m ON 
    fvc.id = m.id
    GROUP BY 
    {aggregation_sql} 
    """

    aggregation_results_df = con.execute(aggregation_query).df().query("final_dollar_value != 0")

    figsize = (10, 5)
    if include_id_grouping_filter:
        num_ids = len(aggregation_results_df['id'].unique())
        figsize = (10, 3 * num_ids)
        
    con.close()
    
    #st.dataframe(aggregation_results_df, use_container_width=True, hide_index=True)

    fig = waterfall_multitier_fig(
        df = aggregation_results_df,
        col = 'final_dollar_value',
        category = aggregation_filter,
        tiers = 'id' if include_id_grouping_filter else None,
        sorting_list = None,
        sort_directions = None,
        figsize = figsize,
        include_line = False,
        include_value_labels = True,
        value_labels_decimals = 0,
        title = "Benefit and Cost Breakdown",
        annotations = [None],
        ylabel = 'Dollars ($)',
        ylims = None,
    )
    st.pyplot(fig, clear_figure=True)

else:
    st.info("OpenBCA outputs not found. Run the OpenBCA model to generate outputs.")
