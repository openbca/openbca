from pandas.core.dtypes.cast import CategoricalDtype
import streamlit as st 
import os
from pathlib import Path
import duckdb
import pandas as pd
import numpy as np
from figures import waterfall_multitier_fig, hour_of_day_ls_fig, bar_fig

st.set_page_config(layout="wide")

col1, col2, col3, col4, col5 = st.columns(5)

LOGOS_DIR = Path(__file__).resolve().parents[1] / "logos"
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
OUTPUT_DIR = REPO_ROOT / "output"

# Match Makefile defaults (DB?=output/openbca.db, DBV?=output/openbca_input_validation.db) if not set.
DEFAULT_OUTPUT_DB = REPO_ROOT / "output" / "openbca.db"
DEFAULT_OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)

db_value = os.environ.get("DB", str(DEFAULT_OUTPUT_DB))
db_path = Path(db_value).expanduser()

st.title("OpenBCA Insights and Analysis")
st.markdown("### Explore the results of your Jurisdiction Specific Test")
db_exists_now = db_path.exists()

if db_exists_now:
    con = duckdb.connect(str(db_path), read_only=True)

    st.sidebar.title("Filter Results")

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
    
    filters = []
    for col in measure_filters_df.columns:
        if len(measure_filters_df[col].unique()) > 1:
            filters.append(col)
    
    num_filters = len(filters)

    if num_filters == 0:
        pass
    else:
        # If there are more than 5 filters, create multiple rows of filters.
        max_filters_per_row = 5
        num_filter_rows = int(np.ceil(num_filters/max_filters_per_row))
        # Create between 3 and 5 columns depending on the number of filter options.
        with st.form("Apply Selectios", border=True):
            #st.markdown("##### Apply Filters")
            cols = st.columns(min(max(num_filters, 3), 5))
            #st.markdown("##### Upload Input Files")
            filters_dict = {}
            filters_options_dict = {}
            for j in range(num_filter_rows):
                for i in range(num_filters):
                    with cols[i]:
                        category = filters[j*max_filters_per_row + i]
                        options = measure_filters_df[category].unique().tolist()
                        filters_options_dict[category] = options
                        filters_dict[category] = st.multiselect(
                            label = f"Limit {' '.join(category.split('_')).title()} to:".replace(" Id ", " ID "),
                            options = options,
                            key = f"filter_{category}",
                        )

                        if len(filters_dict[category]) == 0:
                            filters_dict[category] = options  

            filter_submitted = st.form_submit_button("Filter Results")

    where_sql = f"WHERE 1=1"
    for category, values in filters_dict.items():
        if len(values) < len(filters_options_dict[category]):
            where_snippet = ', '.join(["'{}'".format(value) for value in values])
            where_sql += f" AND m.{category} IN ({where_snippet})"

    jst_query = f"""
    SELECT 
    SUM(total_costs) AS total_costs
    , SUM(total_benefits) AS total_benefits
    , SUM(total_net_benefits) AS total_net_benefits
    , -SUM(total_benefits) / SUM(total_costs) AS jst_ratio
    FROM 
    openbca.core_layer3_finalization.results_summary_by_id m
    {where_sql} 
    """

    jst_results_df = con.execute(jst_query).df()

    jst_ratio = jst_results_df['jst_ratio'].values[0]
    total_costs = -jst_results_df['total_costs'].values[0]
    total_benefits = jst_results_df['total_benefits'].values[0]
    net_benefits = jst_results_df['total_net_benefits'].values[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Benefits", value=f"${total_benefits:,.0f}", border=False)
    col2.metric(label="Total Costs", value=f"${total_costs:,.0f}", border=False)
    col3.metric(label="Net Benefits", value=f"${net_benefits:,.0f}", border=False)
    col4.metric(label="JST Ratio", value=f"{jst_ratio:.2f}", border=False)
    
    aggregation_options = ["Commodity", "Value Stream"]
    
    col1, col2 = st.columns(spec=[0.5, 0.5], gap="medium", border=True)

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

        if commodity_filter == 'ELECTRIC':
            unit = 'kWh'
        elif commodity_filter in ['NATURAL GAS', 'PROPANE', 'OIL', 'DIESEL']:
            unit = 'MMBtu'
        else:
            unit = ''
        
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

        temporal_aggregation_benefits_sql = f"""
        WITH benefits AS (
        SELECT 
        {temporal_aggregation_filter}
        , sum(final_dollar_value) as final_dollar_value
        , sum(net_energy_savings) as net_energy_savings
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        GROUP BY 
        {temporal_aggregation_filter}
        )
        """

        temporal_aggregation_savings_sql = f"""
        , savings AS (
        SELECT 
        {temporal_aggregation_filter}
        , sum(net_energy_savings) as net_lifecycle_energy_savings
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fsc
        JOIN openbca.core_layer0_base.measures m ON 
        fsc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        AND value_stream IN ('Energy Generation (E)', 'Fuel Supply and O&M (NG)', 'Propane Supply', 'Oil Supply', 'Diesel Supply')
        GROUP BY 
        {temporal_aggregation_filter}
        )
        """

        if unit == '':
            temporal_aggregation_query = f"""
            {temporal_aggregation_benefits_sql}
            select
            *
            from benefits
            """
            
        else:
            temporal_aggregation_query = f"""
            {temporal_aggregation_benefits_sql}
            {temporal_aggregation_savings_sql}
            SELECT 
            b.*
            , s.net_lifecycle_energy_savings
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

        costs_query = f"""
        SELECT 
        commodity
        , - sum(final_dollar_value) AS final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
        GROUP BY 
        commodity
        """

        costs_results_df = con.execute(costs_query).df()

        temporal_aggregation_bar_fig = bar_fig(
        df = temporal_aggregation_results_df,
        col = 'final_dollar_value',
        category = temporal_aggregation_filter,
        groupings = None,
        uncertainty_col = None,
        figsize= (10, 6),
        y2_col = None if unit == '' else 'net_lifecycle_energy_savings',
        min_y2_counts = 0,
        pin_yaxis_zeros = True,
        single_bar_color="cornflowerblue",
        horizontal = False,
        space_fraction = 0.65,
        sort_by = None,
        sort_ascending = True,
        title = f"Benefits by {temporal_aggregation_filter.title().replace('_', ' ')}",
        xlabel = None,
        ylabel = '$ Benefits',
        y2label = f'Savings ({unit})',
        ax = None,
        legend = True,
        legend_loc = None,
        label_map = None
        )

        st.pyplot(temporal_aggregation_bar_fig, clear_figure=True)

        costs_bar_fig = bar_fig(
        df = costs_results_df,
        col = 'final_dollar_value',
        category = 'commodity',
        groupings = None,
        uncertainty_col = None,
        figsize= (10, 6),
        y2_col = None,
        min_y2_counts = 0,
        pin_yaxis_zeros = True,
        single_bar_color="darkred",
        horizontal = True,
        space_fraction = 0.65,
        sort_by = None,
        sort_ascending = True,
        title = f"Costs by Type",
        xlabel = None,
        ylabel = '$ Costs',
        y2label = None,
        ax = None,
        legend = True,
        legend_loc = None,
        label_map = {'ADMIN': 'Administration', 'UTILITY INCENTIVE': 'Utility Incentive', 'MEASURE COST': 'Measure Cost', 'TAX INCENTIVE': 'Tax Incentive'}
        )

        st.pyplot(costs_bar_fig, clear_figure=True)

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

st.write(f"Using Database: `{db_value}`")