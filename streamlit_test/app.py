import streamlit as st 
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import duckdb
import pandas as pd
import numpy as np
from figures import waterfall_multitier_fig

col1, col2, col3 = st.columns(3)

LOGOS_DIR = Path(__file__).resolve().parent / "logos"
with col1:
    logo_col, _spacer_col = st.columns([2, 1])
    with logo_col:
        st.image(str(LOGOS_DIR / "NASEO.jpg"), use_container_width=True)
with col2:
    logo_col, _spacer_col = st.columns([1, 1])
    with logo_col:
        st.image(str(LOGOS_DIR / "ICF.jpg"), use_container_width=True)
with col3:
    st.image(str(LOGOS_DIR / "RECURVE.jpg"), use_container_width=True)

st.title("Welcome to the OpenBCA")
st.write("This interface is designed to help you run the OpenBCA model and visualize results.")

# Resolve paths relative to this file, not the current working directory.
REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_TEMPLATES_DIR = REPO_ROOT / "nspm" / "input_templates"
INPUT_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Match Makefile default (DB?=output/openbca.db) if not set.
DEFAULT_DB = REPO_ROOT / "output" / "openbca.db"
DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)

st.subheader("Upload Input Files")
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
        "Overwrite existing output database",
        "Backup existing output database, then run OpenBCA",
        "Keep existing output database",
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

run_clicked = st.button("Run OpenBCA", type="primary")
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
st.subheader("OpenBCA Results Explorer")

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
    #st.dataframe(aggregation_results_df, use_container_width=True, hide_index=True)

    fig = waterfall_multitier_fig(
        df = aggregation_results_df,
        col = 'final_dollar_value_label',
        category = aggregation_column,
        tiers = None,
        sorting_list = ['total', 'final_dollar_value'],
        sort_directions = [True, False],
        figsize = (11, 5),
        include_line = False,
        include_value_labels = True,
        value_labels_decimals = num_bars_sig_figs,
        title = "Benefit and Cost Breakdown",
        annotations = [None],
        ylabel = f'Dollars (${dollar_magnitude_dict[dollar_magnitude]})',
        ylims = None,
    )
    st.pyplot(fig, clear_figure=True)

else:
    st.info("OpenBCA outputs not found. Run the OpenBCA model to generate outputs.")

con.close()