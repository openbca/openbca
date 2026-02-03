from pandas.core.dtypes.cast import CategoricalDtype
import streamlit as st 
import os
from pathlib import Path
import duckdb
import pandas as pd
import numpy as np
from sql_queries import (
    generate_measure_filters_query,
    generate_jst_query, 
    generate_waterfall_query, 
    generate_benefit_cost_scatter_query,
    generate_benefits_commodity_options_query, 
    generate_populated_temporal_cols_query, 
    generate_temporal_aggregation_benefits_query, 
    generate_null_aggregation_benefits_query, 
    generate_value_stream_benefits_query, 
    generate_costs_commodity_query, 
    generate_costs_value_stream_query,
    generate_summary_results_query
)
from figures import (
    waterfall_multitier_fig, 
    hour_of_day_ls_fig, 
    bar_fig, 
    scatter_fig,
    replace_multiple_string_elements
)
from helper_functions import (
    determine_label_sig_figs, 
    determine_dollar_magnitude
)

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
st.markdown("#### Explore the results of your Jurisdiction Specific Test")
db_exists_now = db_path.exists()

if not db_exists_now:
    st.info("OpenBCA outputs not found. Run the OpenBCA model to generate results.")
else:
    con = duckdb.connect(str(db_path), read_only=True)

    measure_filters_df = con.execute(generate_measure_filters_query()).df()
    
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
            cols = st.columns(min(max(num_filters, 3), 5))
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

            filter_submitted = st.form_submit_button("Apply Selection", type="primary")
    
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

    jst_results_df = con.execute(generate_jst_query(where_sql)).df()
    if len(jst_results_df) == 0:
        st.info("No results correspond to the selected filters. Please check your selections.")
    else:
        jst_ratio = jst_results_df['jst_ratio'].values[0]
        total_costs = -jst_results_df['total_costs'].values[0]
        total_benefits = jst_results_df['total_benefits'].values[0]
        net_benefits = jst_results_df['total_net_benefits'].values[0]

        st.markdown("#### JST Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="Total Benefits", value=f"${total_benefits:,.0f}", border=False)
        col2.metric(label="Total Costs", value=f"${total_costs:,.0f}", border=False)
        col3.metric(label="Net Benefits", value=f"${net_benefits:,.0f}", border=False)
        col4.metric(label="JST Ratio", value=f"{jst_ratio:.2f}", border=False)

        st.divider()
        ###Analyis  
        col1, col2 = st.columns(spec=[0.55, 0.45], gap="medium", border=False)
        
        # Waterfall Plot
        with col1: 
            st.markdown("#### Portfolio Analysis")

            waterfall_options = ["Impact Category", "Value Stream"]
            
            waterfall_filter = st.radio(
                label = "See waterfall results by:", 
                options = waterfall_options, 
                horizontal = True,
                index = 0, 
                )

            waterfall_column = waterfall_filter.lower().replace(" ", "_").replace("impact_category", "commodity")

            waterfall_results_df = con.execute(generate_waterfall_query(where_sql, waterfall_column)).df()
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

            st.pyplot(waterfall_fig, clear_figure=True)

            # Benefit and Cost Scatter Plot
        with col2:
            catalog_by_filter = ''
            if num_filters > 0:
                catalog_by_filter = st.radio("Catalog scatter plot results by:", options=[' '.join(filter.split('_')).title().replace(" Id", " ID") for filter in filters if filter != 'id'], index=0, horizontal=True).lower().replace(" ", "_")
                catalog_by_filter_sql = f", {catalog_by_filter.lower().replace(" ", "_")}"

            benefit_cost_scatter_df = con.execute(generate_benefit_cost_scatter_query(where_sql, catalog_by_filter_sql)).df()
            if num_filters > 0:
                benefit_cost_scatter_df[f"{catalog_by_filter}"].fillna("None", inplace=True)
            
            #benefit_cost_scatter_df, benefit_cost_scatter_unit_labels = determine_dollar_magnitude(benefit_cost_scatter_df, x_col='total_costs', y_col='total_benefits') 
            
            min_scatter_val = benefit_cost_scatter_df[['total_costs', 'total_benefits']].min().min()
            max_scatter_val = benefit_cost_scatter_df[['total_costs', 'total_benefits']].max().max()
            scatter_range = max_scatter_val - min_scatter_val
            initial_padding = 0.05
            axis_min = min_scatter_val - initial_padding * scatter_range
            axis_max = max_scatter_val + initial_padding * scatter_range

            x_min_scatter_val = benefit_cost_scatter_df['total_costs'].min()
            x_max_scatter_val = benefit_cost_scatter_df['total_costs'].max()
            y_min_scatter_val = benefit_cost_scatter_df['total_benefits'].min()
            y_max_scatter_val = benefit_cost_scatter_df['total_benefits'].max()

            zoom_padding = 0.005
            x_min = x_min_scatter_val + scatter_range * zoom_padding
            x_max = x_max_scatter_val - scatter_range * zoom_padding
            y_min = y_min_scatter_val + scatter_range * zoom_padding
            y_max = y_max_scatter_val - scatter_range * zoom_padding

            zoom = st.slider("Zoom:", min_value=0.0, max_value=0.999, value=0.0, step=0.001)
            
            plot_x_axis_min = min(axis_min*(1 - zoom), x_max)
            plot_x_axis_max = max(axis_max*(1 - zoom), x_min)
            plot_y_axis_min = min(axis_min*(1 - zoom), y_max)
            plot_y_axis_max = max(axis_max*(1 - zoom), y_min)

            plot_benefit_cost_scatter_df, plot_benefit_cost_scatter_unit_labels, plot_benefit_cost_scatter_scale_exponent = determine_dollar_magnitude(
                benefit_cost_scatter_df.query(
                    f"{plot_x_axis_min} <= total_costs <= {plot_x_axis_max} and {plot_y_axis_min} <= total_benefits <= {plot_y_axis_max}"), 
                    x_col='total_costs', 
                    y_col='total_benefits',
                    return_scale_exponent=True
                    )

            min_marker_size = 100
            max_marker_size = 300 
            marker_size = max(min_marker_size, min(max_marker_size, min_marker_size + 10*(max_marker_size - min_marker_size) / len(plot_benefit_cost_scatter_df)))

            benefit_cost_scatter_fig = scatter_fig(
                df = plot_benefit_cost_scatter_df,
                xy_cols_dict = {
                    'total_costs':{'uncertainty_col':None, 'label': 'Costs ($)'},
                    'total_benefits':{'uncertainty_col':None, 'label': 'Benefits ($)'}
                    },
                marker_size = marker_size,
                color_by_col = catalog_by_filter,
                label_points = False,#True if len(plot_benefit_cost_scatter_df) <= 10 else False,
                labels = plot_benefit_cost_scatter_df['id'].tolist(),
                label_size = 10,
                figsize = (8, 6),
                title = "Benefits and Costs by ID",
                xlims = [plot_x_axis_min/10**plot_benefit_cost_scatter_scale_exponent, plot_x_axis_max/10**plot_benefit_cost_scatter_scale_exponent],
                xlabel = f'Costs {plot_benefit_cost_scatter_unit_labels[0]}',
                ylims = [plot_y_axis_min/10**plot_benefit_cost_scatter_scale_exponent, plot_y_axis_max/10**plot_benefit_cost_scatter_scale_exponent],
                ylabel = f'Benefits {plot_benefit_cost_scatter_unit_labels[1]}',
                legend = True,
                legend_labels = sorted(list(plot_benefit_cost_scatter_df[f"{catalog_by_filter}"].unique())),
                legend_loc = "upper left",
            )

            st.pyplot(benefit_cost_scatter_fig, clear_figure=True)

        st.divider()
        # Benefits and Costs Analysis
        st.markdown("#### Benefits and Costs Analysis")

        col1, col2 = st.columns(spec=[0.55, 0.45], gap="medium", border=True)
        
        # Benefits  
        with col1:
            st.markdown("#### Benefits")
            st.markdown("##### Explore Results by Commodity and Value Stream")

            benefits_commodity_options_df = con.execute(generate_benefits_commodity_options_query(where_sql)).df()
            benefits_commodity_options = [commodity.title().replace("Nei", "NEI") for commodity in benefits_commodity_options_df['commodity'].tolist()]

            commodity_filter = st.radio(
                label = "Select Impact Category:", 
                options = benefits_commodity_options, 
                horizontal = True,
                index = 0 if 'ELECTRIC' not in benefits_commodity_options else benefits_commodity_options.index('ELECTRIC'), 
                )
            
            commodity_filter = commodity_filter.upper()

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
                    con.execute(generate_populated_temporal_cols_query(where_sql, commodity_filter, col)).df()
                ) > 0:
                    populated_temporal_cols.append(col)

            subcol1, subcol2 = st.columns(spec=[0.5, 0.5], gap="medium", border=False)

            temporal_aggregation_filter = subcol1.radio(
                label = "Aggregate results by:",
                options = [' '.join(col.split('_')).title().replace("Of", "of") for col in populated_temporal_cols],
                index = 0,
                horizontal = True,
                )

            temporal_aggregation_filter = temporal_aggregation_filter.lower().replace(" ", "_")
            
            null_aggregation_benefits_df = con.execute(generate_null_aggregation_benefits_query(where_sql, commodity_filter, temporal_aggregation_filter)).df()
            if len(null_aggregation_benefits_df) > 0:
                null_aggregation_benefits = null_aggregation_benefits_df['final_dollar_value'].values[0]
                subcol2.write(f"")
                subcol2.markdown(f"###### Lower granularity benefits = **${null_aggregation_benefits:,.0f}**", help="Benefits that accrue from value streams with lower temporal granularity than displayed in the figure. For example, if monthly benefits are shown, then value streams that can only be quantified at an annual level are accounted for here.")
            
            temporal_aggregation_results_df = con.execute(generate_temporal_aggregation_benefits_query(where_sql, commodity_filter, temporal_aggregation_filter, unit, group_by_value_stream=False)).df()
            temporal_aggregation_results_df, temporal_aggregation_results_unit_labels = determine_dollar_magnitude(temporal_aggregation_results_df, x_col='final_dollar_value', y_col='net_lifecycle_energy_savings' if unit != '' else None)
            temporal_aggregation_value_stream_results_df = con.execute(generate_temporal_aggregation_benefits_query(where_sql, commodity_filter, temporal_aggregation_filter, unit, group_by_value_stream=True)).df()
            temporal_aggregation_value_stream_results_df, temporal_aggregation_value_stream_results_unit_labels = determine_dollar_magnitude(temporal_aggregation_value_stream_results_df, x_col='final_dollar_value', y_col='net_lifecycle_energy_savings' if unit != '' else None)
            
            value_streams = sorted(temporal_aggregation_value_stream_results_df['value_stream'].unique().tolist())
            
            if 'show_value_streams_filter' not in st.session_state:
                st.session_state.show_value_streams_filter = None
            
            if len(value_streams) > 1:
                st.session_state.show_value_streams_filter = st.multiselect(
                    label = f"Select Value Streams to Show:",
                    options = value_streams,
                    key = "value_streams_filter",
                    default = None
                )
            
            temporal_aggregation_bar_fig = bar_fig(
                df = temporal_aggregation_results_df,
                col = 'final_dollar_value',
                category = temporal_aggregation_filter,
                value_stream_df = temporal_aggregation_value_stream_results_df.query(f"value_stream in {st.session_state.show_value_streams_filter}") if len(value_streams) > 1 else None,
                figsize= (10, 6),
                y2_col = None if unit == '' else 'net_lifecycle_energy_savings',
                pin_yaxis_zeros = True,
                single_bar_color="cornflowerblue",
                space_fraction = 0.65,
                title = f"Benefits by {temporal_aggregation_filter.title().replace('_', ' ')}",
                xlabel = None,
                ylabel = f'Benefits {temporal_aggregation_results_unit_labels[0]}',
                y2label = f'Savings ({temporal_aggregation_results_unit_labels[1][2] if len(temporal_aggregation_results_unit_labels[1]) > 2 else ''}{unit})',
                legend = True,
                legend_loc = None,
            )

            st.pyplot(temporal_aggregation_bar_fig, clear_figure=True)
            
            value_stream_benefits_df = con.execute(generate_value_stream_benefits_query(where_sql, commodity_filter)).df()
            st.dataframe(   
                value_stream_benefits_df, 
                width='stretch',
                hide_index=True,
                column_config={
                    'final_dollar_value': st.column_config.NumberColumn(
                        label = "Benefits ($)",
                        format="dollar",
                        )
                    }
                )

        # Costs
        with col2:
            st.markdown("#### Costs")
            st.markdown("##### See Results by Commodity and Value Stream")

            costs_commoidty_results_df = con.execute(generate_costs_commodity_query(where_sql)).df()
            costs_commoidty_results_df, costs_commoidty_results_df_unit_labels = determine_dollar_magnitude(costs_commoidty_results_df, x_col='final_dollar_value', y_col=None)
            costs_commoidty_results_df['commodity'] = costs_commoidty_results_df['commodity'].apply(lambda x: replace_multiple_string_elements(' '.join(x.split('_')).title()))
            
            costs_bar_fig = bar_fig(
                df = costs_commoidty_results_df,
                col = 'final_dollar_value',
                category = 'commodity',
                figsize= (9, 5),
                pin_yaxis_zeros = True,
                single_bar_color="darkred",
                horizontal = True,
                space_fraction = 0.65,
                title = f"Costs by Type",
                xlabel = '',
                ylabel = f'Costs {costs_commoidty_results_df_unit_labels[0]}',
                y2label = None,
                legend = True,
                legend_loc = None,
            )

            st.pyplot(costs_bar_fig, clear_figure=True)

            costs_value_stream_results_df = con.execute(generate_costs_value_stream_query(where_sql)).df()#.rename(columns={'final_dollar_value': 'Costs ($)'})
            costs_value_stream_results_df['Value Stream'] = costs_value_stream_results_df['Value Stream'].apply(lambda x: replace_multiple_string_elements(' '.join(x.split('_')).title()))
            st.dataframe(
                costs_value_stream_results_df, 
                width='stretch', 
                hide_index=True, 
                column_config={
                    'final_dollar_value': st.column_config.NumberColumn(
                        label="Costs ($)",
                        format="dollar",
                        #decimals = 0,
                        )
                    }
                )
    
    st.divider()
    summary_results_df = con.execute(generate_summary_results_query()).df()
    st.markdown("### Summary Results Table:")
    st.dataframe(summary_results_df, width='stretch', hide_index=True)
    st.write(f"Using Database: `{db_value}`")
    con.close()

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