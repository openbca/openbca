from pandas.core.dtypes.cast import CategoricalDtype
import streamlit as st 
import os
from pathlib import Path
import duckdb
import pandas as pd
import numpy as np
from figures import waterfall_multitier_fig, hour_of_day_ls_fig, bar_fig, scatter_fig
from helper_functions import determine_label_sig_figs, determine_dollar_magnitude

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
    
    filter_warning = 'Active filters: '
    for i, (category, values) in enumerate(filters_dict.items()):
        if len(values) < len(filters_options_dict[category]):
            filter_warning += f"{category.title().replace('_', ' ').replace( 'Id', ' ID')}, " 
    if filter_warning != 'Active filters: ':
        st.warning(filter_warning.rstrip(', '))

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
    
    waterfall_options = ["Commodity", "Value Stream"]
    
    col1, col2 = st.columns(spec=[0.5, 0.5], gap="medium", border=True)

    with col1:
        st.markdown("#### Portfolio Analysis")
        waterfall_filter = st.radio(
            label = "See waterfall results by:", 
            options = waterfall_options, 
            horizontal = True,
            index = 0, 
            )

        waterfall_column = waterfall_filter.lower().replace(" ", "_")
            
        waterfall_query = f"""
        SELECT 
        {waterfall_column} 
        , sum(final_dollar_value) as final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        GROUP BY 
        {waterfall_column} 
        """

        waterfall_results_df = con.execute(waterfall_query).df().query("final_dollar_value != 0")
        waterfall_results_total_df = pd.DataFrame([['total', waterfall_results_df['final_dollar_value'].sum()]], columns=[waterfall_column, 'final_dollar_value'])
        waterfall_results_df = pd.concat([waterfall_results_df, waterfall_results_total_df])
        waterfall_results_df['total'] = waterfall_results_df[waterfall_column].apply(lambda x: True if x == 'total' else False)

        waterfall_results_df, waterfall_unit_labels = determine_dollar_magnitude(waterfall_results_df, y_col='final_dollar_value')
        
        num_bars = len(waterfall_results_df)
        num_bars_sig_figs = determine_label_sig_figs(num_bars)

        waterfall_fig = waterfall_multitier_fig(
            df = waterfall_results_df,
            col = 'final_dollar_value',
            category = waterfall_column,
            tiers = None,
            sorting_list = ['total', 'final_dollar_value'],
            sort_directions = [True, False],
            figsize = (11, 6),
            include_line = False,
            include_value_labels = True,
            value_labels_decimals = num_bars_sig_figs,
            title = "Benefit and Cost Breakdown",
            annotations = [None],
            ylabel = f'Dollars {waterfall_unit_labels[1]}',
            ylims = None,
        )


        #st.write(aggregation_query)
        st.pyplot(waterfall_fig, clear_figure=True)

        catalog_by_filter = ''
        if num_filters > 0:
            catalog_by_filter = st.radio("Catalog scatter plot results by:", options=[' '.join(filter.split('_')).title() for filter in filters if filter != 'id'], index=0, horizontal=True).lower().replace(" ", "_")
            catalog_by_filter_sql = f", {catalog_by_filter.lower().replace(" ", "_")}"

        benefit_cost_scatter_query = f"""
        SELECT 
        id
        {catalog_by_filter_sql}
        , total_benefits
        , -total_costs AS total_costs
        FROM 
        openbca.core_layer3_finalization.results_summary_by_id m
        {where_sql} 
        """
        
        benefit_cost_scatter_df = con.execute(benefit_cost_scatter_query).df()
        if num_filters > 0:
            benefit_cost_scatter_df[f"{catalog_by_filter}"].fillna("None", inplace=True)
        
        benefit_cost_scatter_df, benefit_cost_scatter_unit_labels = determine_dollar_magnitude(benefit_cost_scatter_df, x_col='total_costs', y_col='total_benefits')

        min_marker_size = 100
        max_marker_size = 300  

        marker_size = max(min_marker_size, min(max_marker_size, min_marker_size + 10*(max_marker_size - min_marker_size) / len(benefit_cost_scatter_df)))
        
        min_scatter_val = benefit_cost_scatter_df[['total_costs', 'total_benefits']].min().min()
        max_scatter_val = benefit_cost_scatter_df[['total_costs', 'total_benefits']].max().max()
        scatter_range = max_scatter_val - min_scatter_val
        range_multiplier = 0.07
        axis_min = min_scatter_val - range_multiplier * scatter_range
        axis_max = max_scatter_val + range_multiplier * scatter_range

        zoom = st.slider("Zoom:", min_value=0.0, max_value=0.98, value=0.0, step=0.01)

        benefit_cost_scatter_fig = scatter_fig(
            df = benefit_cost_scatter_df,
            xy_cols_dict = {
                'total_costs':{'uncertainty_col':None, 'label': 'Costs ($)'},
                'total_benefits':{'uncertainty_col':None, 'label': 'Benefits ($)'}
            },
            marker_size = marker_size,
            include_line = False,
            vlines = [None],
            # marker: str = markers_open[0],
            # marker_color: str = colors[3],
            color_by_col = catalog_by_filter,
            label_points = True if len(benefit_cost_scatter_df) <= 10 else False,
            labels = benefit_cost_scatter_df['id'].tolist(),
            label_size = 10,
            figsize = (9, 7),
            title = "Benefits and Costs by ID",
            xlims = [axis_min*(1 - zoom), axis_max*(1 - zoom)],
            xlabel = f'Costs {benefit_cost_scatter_unit_labels[0]}',
            ylims = [axis_min*(1 - zoom), axis_max*(1 - zoom)],
            ylabel = f'Benefits {benefit_cost_scatter_unit_labels[1]}',
            legend = True,
            legend_labels = sorted(list(benefit_cost_scatter_df[f"{catalog_by_filter}"].unique())),
            legend_loc = "upper left",
        )

        st.pyplot(benefit_cost_scatter_fig, clear_figure=True)

    with col2:
        st.markdown("#### Benefits Analysis")
        st.markdown("##### Explore Results by Commodity and Value Stream")

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
        
        col1, col2 = st.columns(spec=[0.55, 0.45], gap="medium", border=False)

        temporal_aggregation_filter = col1.radio(
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
            , sum(final_dollar_value) AS final_dollar_value
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
            , sum(net_energy_savings) AS net_lifecycle_energy_savings
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
            """

        null_aggregation_benefits_query = f"""
            SELECT 
            sum(final_dollar_value) AS final_dollar_value
            FROM 
            openbca.core_layer3_finalization.final_value_calculations_ts fvc 
            JOIN openbca.core_layer0_base.measures m ON 
            fvc.id = m.id
            {where_sql} 
            AND commodity = '{commodity_filter}'
            AND {temporal_aggregation_filter} IS NULL
            HAVING SUM(final_dollar_value) IS NOT NULL
            """
        
        null_aggregation_benefits_df = con.execute(null_aggregation_benefits_query).df()
        if len(null_aggregation_benefits_df) > 0:
            null_aggregation_benefits = null_aggregation_benefits_df['final_dollar_value'].values[0]
            col2.write(f"")
            col2.write(f"Lower granularity benefits = **${null_aggregation_benefits:,.0f}**")

        temporal_aggregation_results_df = con.execute(temporal_aggregation_query).df()
        temporal_aggregation_results_df, temporal_aggregation_results_unit_labels = determine_dollar_magnitude(temporal_aggregation_results_df, x_col='final_dollar_value', y_col='net_lifecycle_energy_savings' if unit != '' else None)

        value_stream_benefits_sql = f"""
            SELECT 
            value_stream as '{commodity_filter.title()} Value Stream'
            , sum(final_dollar_value) AS 'Benefits ($)'
            FROM 
            openbca.core_layer3_finalization.final_value_calculations_ts fvc 
            JOIN openbca.core_layer0_base.measures m ON 
            fvc.id = m.id
            {where_sql} 
            AND commodity = '{commodity_filter}'
            GROUP BY 
            value_stream
        """

        value_stream_benefits_df = con.execute(value_stream_benefits_sql).df()

        costs_commodity_query = f"""
            SELECT 
            commodity
            , -sum(final_dollar_value) AS final_dollar_value
            FROM 
            openbca.core_layer3_finalization.final_value_calculations_ts fvc 
            FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
            fvc.id = m.id
            {where_sql} 
            AND commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
            GROUP BY 
            commodity
            HAVING ABS(final_dollar_value) > 0
        """

        costs_value_stream_query = f"""
            SELECT 
            value_stream AS 'Value Stream'
            , -sum(final_dollar_value) AS final_dollar_value
            FROM 
            openbca.core_layer3_finalization.final_value_calculations_ts fvc 
            FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
            fvc.id = m.id
            {where_sql} 
            AND commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
            GROUP BY 
            value_stream
            HAVING ABS(final_dollar_value) > 0
        """

        costs_commoidty_results_df = con.execute(costs_commodity_query).df()
        costs_commoidty_results_df, costs_commoidty_results_df_unit_labels = determine_dollar_magnitude(costs_commoidty_results_df, x_col='final_dollar_value', y_col=None)

        costs_value_stream_results_df = con.execute(costs_value_stream_query).df()

        temporal_aggregation_bar_fig = bar_fig(
            df = temporal_aggregation_results_df,
            col = 'final_dollar_value',
            category = temporal_aggregation_filter,
            groupings = None,
            uncertainty_col = None,
            figsize= (10, 6),
            y2_col = None if unit == '' else 'net_lifecycle_energy_savings',
            min_y2_counts = None,  # allow negative net_lifecycle_energy_savings on y2
            pin_yaxis_zeros = True,
            single_bar_color="cornflowerblue",
            horizontal = False,
            space_fraction = 0.65,
            sort_by = None,
            sort_ascending = True,
            title = f"Benefits by {temporal_aggregation_filter.title().replace('_', ' ')}",
            xlabel = None,
            ylabel = f'Benefits {temporal_aggregation_results_unit_labels[0]}',
            y2label = f'Savings ({temporal_aggregation_results_unit_labels[1][2] if len(temporal_aggregation_results_unit_labels[1]) > 2 else ''}{unit})',
            ax = None,
            legend = True,
            legend_loc = None,
            label_map = None
        )

        st.pyplot(temporal_aggregation_bar_fig, clear_figure=True)

        st.dataframe(value_stream_benefits_df, width='stretch', hide_index=True)

        st.divider()
        st.markdown("#### Costs Analysis")
        st.markdown("##### Explore Results by Commodity and Value Stream")
        costs_bar_fig = bar_fig(
            df = costs_commoidty_results_df,
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
            xlabel = '',
            ylabel = f'Costs {costs_commoidty_results_df_unit_labels[0]}',
            y2label = None,
            ax = None,
            legend = True,
            legend_loc = None,
            label_map = {'ADMIN': 'Administration', 'UTILITY INCENTIVE': 'Utility Incentive', 'MEASURE COST': 'Measure Cost', 'TAX INCENTIVE': 'Tax Incentive'}
        )

        st.pyplot(costs_bar_fig, clear_figure=True)

        st.dataframe(costs_value_stream_results_df, width='stretch', hide_index=True)

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
else:
    st.info("OpenBCA outputs not found. Run the OpenBCA model to generate results.")

st.divider()
st.markdown("### Summary Results Table:")
st.dataframe(con.execute("select * from openbca.core_layer3_finalization.results_summary_by_id").df(), width='stretch', hide_index=True)
st.write(f"Using Database: `{db_value}`")
con.close()