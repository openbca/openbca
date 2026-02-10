from typing import Any
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
    generate_multiple_options_probe_query, 
    generate_categorical_summary_query,
    generate_costs_commodity_query, 
    generate_costs_value_stream_query,
    generate_summary_results_query
)
from figures import (
    replace_multiple_string_elements,
    waterfall_multitier_fig, 
    hour_of_day_ls_fig, 
    numeric_bar_fig, 
    categorical_bar_fig,
    scatter_fig,
    pie_chart,
)
from helper_functions import (
    space_and_title,
    reconstruct_column_name,
    determine_label_sig_figs, 
    determine_dollar_magnitude,
    generate_all_row_combinations_df
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
    with duckdb.connect(str(db_path), read_only=True) as con:

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
            num_filter_rows = int(np.ceil(num_filters / max_filters_per_row))

            def where_sql_for_others(exclude_category: str) -> str:
                """Build WHERE clause from all filter selections except exclude_category (so options for that dimension reflect other filters)."""
                sql = "WHERE 1=1"
                for other in filters:
                    if other == exclude_category:
                        continue
                    others_selection = st.session_state.get(f"filter_{other}") or []
                    if others_selection:
                        snippet = ", ".join(["'{}'".format(v) for v in others_selection])
                        sql += f" AND m.{other} IN ({snippet})"
                return sql

            where_sql = "WHERE 1=1"
            filters_dict = {}
            filters_options_dict = {}
            with st.container(border=True):
                
                st.markdown("##### Comprehensive Filters", help="Make desired selections and apply them via the 'Apply Selection' button.")
                st.markdown("###### These selections will be applied to all analyses below.")
                
                for j in range(num_filter_rows):
                    start_idx = j * max_filters_per_row
                    num_cols_this_row = min(max_filters_per_row, num_filters - start_idx)
                    cols = st.columns(min(max(num_cols_this_row, 3), 5))
                    for i in range(num_cols_this_row):
                        with cols[i]:
                            category = filters[start_idx + i]
                            # Options for this category = values that exist given ALL OTHER filters' current selections
                            options = sorted(
                                con.execute(
                                    generate_measure_filters_query(where_sql_for_others(category))
                                ).df()[category].unique().tolist()
                            )
                            filters_options_dict[category] = options
                            # Default = current selection restricted to currently available options
                            current_selection = st.session_state.get(f"filter_{category}") or []
                            default = [v for v in current_selection if v in options] if current_selection else []
                            filters_dict[category] = st.multiselect(
                                label=f"Limit {space_and_title(category)} to:",
                                options=options,
                                default=default,
                                key=f"filter_{category}",
                            )
                            if len(filters_dict[category]) == 0:
                                filters_dict[category] = options
                            if len(filters_dict[category]) < len(filters_options_dict[category]):
                                where_snippet = ", ".join(["'{}'".format(value) for value in filters_dict[category]])
                                where_sql += f" AND m.{category} IN ({where_snippet})"


        jst_results_df = con.execute(generate_jst_query(where_sql)).df()
        if len(jst_results_df) == 0:
            st.error("No results correspond to the selected filters. Please check your selections.")
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
            
            with col1: 

                subcol1, subcol2 = st.columns(spec=[0.35, 0.65], gap="medium", border=False)
                with subcol1:
                    st.write(f"")
                    st.markdown("#### Portfolio Analysis")
                
                # Waterfall Plot
                with subcol2:    
                    waterfall_scatter_fig_or_table = st.segmented_control(
                        label = "**Display**", 
                        options = ['Figures', 'Tables'], 
                        default='Figures',
                        key = "waterfall_scatter_fig_or_table"
                        )   
  

                waterfall_options = ["Impact Category", "Value Stream"]
                
                #with subcol2:
                waterfall_filter = st.radio(
                    label = "**Waterfall Steps**", 
                    options = waterfall_options, 
                    horizontal = True,
                    index = 0, 
                    )

                waterfall_column = reconstruct_column_name(waterfall_filter).replace("impact_category", "commodity")

                waterfall_results_df = con.execute(generate_waterfall_query(where_sql, waterfall_column)).df()
                waterfall_results_total_df = pd.DataFrame([['total', waterfall_results_df['final_dollar_value'].sum()]], columns=[waterfall_column, 'final_dollar_value'])
                waterfall_results_df = pd.concat([waterfall_results_df, waterfall_results_total_df])
                waterfall_results_df['total'] = waterfall_results_df[waterfall_column].apply(lambda x: True if x == 'total' else False)

                waterfall_results_df, waterfall_unit_labels = determine_dollar_magnitude(waterfall_results_df, y_col='final_dollar_value')

                num_bars = len(waterfall_results_df)
                num_bars_sig_figs = determine_label_sig_figs(num_bars)

                if waterfall_scatter_fig_or_table == 'Figures':
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

                else:
                    waterfall_results_df.sort_values(by=['total', 'final_dollar_value'], ascending=[True, False], inplace=True)
                    waterfall_results_df[waterfall_column] = waterfall_results_df[waterfall_column].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
                
                    st.dataframe(
                        waterfall_results_df[[waterfall_column, 'final_dollar_value_original']], 
                        width='stretch', 
                        hide_index=True,
                        column_config={
                            waterfall_column: st.column_config.TextColumn(
                                label=space_and_title(waterfall_column),
                            ),
                            'final_dollar_value_original': st.column_config.NumberColumn(
                                label="Dollars ($)",
                                format="dollar",
                            )
                        }
                        )

            # Benefit and Cost Scatter Plot
            with col2:
                catalog_by_filter = ''
                if num_filters > 0:
                    catalog_by_filter = st.radio(
                        "**Create Categories From**", 
                        options = [space_and_title(filter) for filter in filters if filter != 'id'], 
                        index = 0, 
                        horizontal = True,
                    )

                benefit_cost_scatter_df = con.execute(generate_benefit_cost_scatter_query(where_sql, reconstruct_column_name(catalog_by_filter))).df()
                if num_filters > 0:
                    benefit_cost_scatter_df[f"{reconstruct_column_name(catalog_by_filter)}"].fillna("None", inplace=True)

                if waterfall_scatter_fig_or_table == 'Figures':            
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
                        color_by_col = reconstruct_column_name(catalog_by_filter),
                        label_points = False,
                        labels = plot_benefit_cost_scatter_df['id'].tolist(),
                        label_size = 10,
                        figsize = (8, 6),
                        title = "Benefits and Costs by ID",
                        xlims = [plot_x_axis_min/10**plot_benefit_cost_scatter_scale_exponent, plot_x_axis_max/10**plot_benefit_cost_scatter_scale_exponent],
                        xlabel = f'Costs {plot_benefit_cost_scatter_unit_labels[0]}',
                        ylims = [plot_y_axis_min/10**plot_benefit_cost_scatter_scale_exponent, plot_y_axis_max/10**plot_benefit_cost_scatter_scale_exponent],
                        ylabel = f'Benefits {plot_benefit_cost_scatter_unit_labels[1]}',
                        legend = True,
                        legend_labels = sorted(list(plot_benefit_cost_scatter_df[f"{reconstruct_column_name(catalog_by_filter)}"].unique())),
                        legend_loc = "upper left",
                    )

                    st.pyplot(benefit_cost_scatter_fig, clear_figure=True)
                else:
                    benefit_cost_scatter_df.sort_values(by=[reconstruct_column_name(catalog_by_filter), 'total_benefits'], ascending=[True, False], inplace=True)
                    benefit_cost_scatter_df[reconstruct_column_name(catalog_by_filter)] = benefit_cost_scatter_df[reconstruct_column_name(catalog_by_filter)].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))

                    st.dataframe(
                        benefit_cost_scatter_df[['id', reconstruct_column_name(catalog_by_filter), 'total_costs', 'total_benefits']], 
                        width='stretch', 
                        hide_index=True,
                        column_config={
                            reconstruct_column_name(catalog_by_filter): st.column_config.TextColumn(
                                label=space_and_title(reconstruct_column_name(catalog_by_filter)),
                            ),
                            'total_costs': st.column_config.NumberColumn(
                                label="Costs ($)",
                                format="dollar",
                            ),
                            'total_benefits': st.column_config.NumberColumn(
                                label="Benefits ($)",
                                format="dollar",
                            )
                        }
                    )

            st.divider()
            # Benefits and Costs Analysis

            header_col1, header_col2 = st.columns(spec=[0.45, 0.55], gap="medium", border=False)
            with header_col1:
                st.markdown("#### Benefits Analysis")
                st.markdown("##### Explore Results by Impact Category and Value Stream")
            
            with header_col2:    
                bar_pie_fig_or_table = st.segmented_control(
                    label = "**Display**", 
                    options = ['Figures', 'Tables'], 
                    default='Figures',
                    key = "bar_pie_fig_or_table"
                    ) 

            benefits_commodity_options_df = con.execute(generate_benefits_commodity_options_query(where_sql)).df()
            
            benefits_commodity_options = [space_and_title(commodity) for commodity in benefits_commodity_options_df['commodity'].tolist()]

            commodity_filter = st.radio(
                label = "**Impact Category**", 
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

            temporal_aggregation_filter = 'year'

            col1, col2 = st.columns(spec=[0.58, 0.42], gap="medium", border=False)

            # Benefits  
            with col1:  

                if len(populated_temporal_cols) > 1:
                    subcol1, subcol2, subcol3 = st.columns(spec=[0.45, 0.5, 0.05], gap="medium", border=False)

                    temporal_aggregation_filter = subcol1.radio(
                        label = "**Aggregation**",
                        options = [space_and_title(col) for col in populated_temporal_cols],
                        index = 0,
                        horizontal = True,
                        )

                    if len(populated_temporal_cols) > 1:
                        temporal_aggregation_filter = reconstruct_column_name(temporal_aggregation_filter)
                        
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
                        label = f"Show Specific Value Streams:",
                        options = value_streams,
                        key = "value_streams_filter",
                        default = None
                    )
                
                if bar_pie_fig_or_table == 'Figures':
                    temporal_aggregation_bar_fig = numeric_bar_fig(
                        df = temporal_aggregation_results_df,
                        col = 'final_dollar_value',
                        category = temporal_aggregation_filter,
                        value_stream_df = temporal_aggregation_value_stream_results_df.query(f"value_stream in {st.session_state.show_value_streams_filter}") if len(st.session_state.show_value_streams_filter) > 0 else None,
                        figsize= (10, 6),
                        y2_col = None if unit == '' else 'net_lifecycle_energy_savings',
                        pin_yaxis_zeros = True,
                        single_bar_color="cornflowerblue",
                        space_fraction = 0.65,
                        title = f"Benefits by {space_and_title(temporal_aggregation_filter)}",
                        xlabel = None,
                        ylabel = f'Benefits{temporal_aggregation_results_unit_labels[0]}',
                        y2label = f'Savings ({temporal_aggregation_results_unit_labels[1][2] if len(temporal_aggregation_results_unit_labels[1]) > 2 else ''}{unit})'.replace('$', ''),
                        legend = True if len(st.session_state.show_value_streams_filter) > 0 else False,
                        legend_loc = None,
                    )

                    st.pyplot(temporal_aggregation_bar_fig, clear_figure=True)

                else:
                    st.dataframe(
                    temporal_aggregation_results_df[[temporal_aggregation_filter,'final_dollar_value_original', 'net_lifecycle_energy_savings_original']],
                    width='stretch',
                    hide_index=True,
                    column_config={
                        temporal_aggregation_filter: st.column_config.NumberColumn(
                            label=space_and_title(temporal_aggregation_filter),
                            format="%.0f",
                        ),
                        'final_dollar_value_original': st.column_config.NumberColumn(
                            label="Benefits ($)",
                            format="dollar",
                        ),
                    'net_lifecycle_energy_savings_original': st.column_config.NumberColumn(
                        label=f'Savings ({temporal_aggregation_results_unit_labels[1][2] if len(temporal_aggregation_results_unit_labels[1]) > 2 else ''}{unit})'.replace('$', ''),
                        format="%.2f",
                        )},
                    )
        
            with col2:
                st.write(f"")
                value_stream_benefits_df = con.execute(generate_value_stream_benefits_query(where_sql, commodity_filter)).df()
                pos_value_stream_benefits_df = value_stream_benefits_df.query("final_dollar_value > 0")
                neg_value_stream_benefits_df = value_stream_benefits_df.query("final_dollar_value < 0")
                st.markdown(f"#### {space_and_title(commodity_filter)} Benefit Value Streams")
                if len(value_stream_benefits_df) == 1:
                    value_stream_benefits = value_stream_benefits_df['final_dollar_value'].values[0]

                    for i in range(11):
                        st.write(f"")
                    
                    st.markdown(f"#### {space_and_title(commodity_filter)} Benefits = **${value_stream_benefits:,.0f}**")

                else:
                    if bar_pie_fig_or_table == 'Figures':
                        
                        if len(pos_value_stream_benefits_df) > 0:
                            pos_value_stream_benefits_df, pos_value_stream_benefits_unit_labels = determine_dollar_magnitude(pos_value_stream_benefits_df, x_col='final_dollar_value', y_col=None)
                        
                        if len(neg_value_stream_benefits_df) > 0:
                            neg_value_stream_benefits_df, neg_value_stream_benefits_unit_labels = determine_dollar_magnitude(neg_value_stream_benefits_df, x_col='final_dollar_value', y_col=None)

                        pie_chart_fig = pie_chart(
                            df = pos_value_stream_benefits_df if len(pos_value_stream_benefits_df) > 0 else neg_value_stream_benefits_df,
                            col = 'final_dollar_value',
                            label_col = 'value_stream',
                            figsize = (9, 5),
                            title = f"{space_and_title(commodity_filter)} Benefits{pos_value_stream_benefits_unit_labels[0] if len(pos_value_stream_benefits_df) > 0 else neg_value_stream_benefits_unit_labels[0]}"
                        )

                        st.pyplot(pie_chart_fig, clear_figure=True)

                        if len(neg_value_stream_benefits_df) > 0 and len(neg_value_stream_benefits_df) < len(pos_value_stream_benefits_df) + len(neg_value_stream_benefits_df):
                            st.markdown("##### Additional Negative Benefits Value Streams")
                            st.dataframe(
                                neg_value_stream_benefits_df[['value_stream', 'final_dollar_value_original']],
                                width='stretch',
                                hide_index=True,
                                column_config={
                                    'final_dollar_value_original': st.column_config.NumberColumn(
                                        label="Benefits ($)",
                                        format="dollar",
                                    ),
                                    'value_stream': st.column_config.TextColumn(
                                        label = "Value Stream",
                                    )
                                    }
                                )

                    else:
                        st.dataframe(
                            value_stream_benefits_df[['value_stream', 'final_dollar_value']],
                            width='stretch',
                            hide_index=True,
                            column_config={
                                'final_dollar_value': st.column_config.NumberColumn(
                                    label="Benefits ($)",
                                    format="dollar",
                                ),
                                'value_stream': st.column_config.TextColumn(
                                    label = "Value Stream",
                                )
                                }
                            )

    ### Comparative Analysis
        category_filters = con.execute(
            generate_multiple_options_probe_query(
                where_sql, column_names=[filter for filter in filters if filter != 'id']+['commodity']
                )
                ).df().query("distinct_values > 1")['field'].tolist()

        if len(category_filters) > 0:
            st.divider()
            st.markdown("#### Comparative Analysis")
            col1, col2, col3 = st.columns(spec=[0.45, 0.4, 0.15], gap="medium", border=False)

            with col1:
                category_filter = st.radio(
                    label="**Compare Net Benefits (Benefits - Costs) By**",
                    options=[space_and_title(filter) for filter in category_filters],
                    index=0,
                    horizontal=True,
                )

                category_filter_sql = f"{reconstruct_column_name(category_filter)}"

                categorical_summary_df = con.execute(generate_categorical_summary_query(where_sql, category_filter_sql)).df().query(f"not {category_filter_sql}.isnull()")
                categorical_summary_df, categorical_summary_unit_labels = determine_dollar_magnitude(categorical_summary_df, x_col='final_dollar_value', y_col=None)        
                categorical_summary_df[f"{category_filter_sql}"] = categorical_summary_df[f"{category_filter_sql}"].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
                
                remaining_category_filters = [filter for filter in category_filters if filter != category_filter_sql]

                categorical_bar_radio_options = {'None': [categorical_summary_df, categorical_summary_unit_labels]}

            with col2:    
                for grouping_filter in remaining_category_filters:

                    categorical_grouping_summary_df = con.execute(generate_categorical_summary_query(where_sql, category_filter_sql, grouping_filter = grouping_filter)).df().query(f"not {grouping_filter}.isnull()")
                    
                    if len(categorical_grouping_summary_df) > len(categorical_summary_df):
                        categorical_grouping_summary_df, categorical_grouping_summary_unit_labels = determine_dollar_magnitude(categorical_grouping_summary_df, x_col='final_dollar_value', y_col=None)
                        categorical_grouping_summary_df[f"{grouping_filter}"] = categorical_grouping_summary_df[f"{grouping_filter}"].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
                        
                        categorical_bar_radio_options[space_and_title(grouping_filter)] = [categorical_grouping_summary_df, categorical_grouping_summary_unit_labels]
                
                grouping_option = 'None'        
                if len(categorical_bar_radio_options.keys()) > 1:
                    grouping_option = st.radio(
                        label = "**Break Out Results By**",
                        options = categorical_bar_radio_options.keys(),
                        index = 0,
                        horizontal = True,
                    )

            col1, col2 = st.columns(spec=[0.6, 0.4], gap="medium", border=False)

            with col1:
                plot_df = generate_all_row_combinations_df(
                    df=categorical_bar_radio_options[grouping_option][0], 
                    col_1=category_filter_sql, 
                    col_2=reconstruct_column_name(grouping_option), 
                    numeric_cols=['final_dollar_value', 'final_dollar_value_original']
                    ).rename(columns={'final_dollar_value_original': 'Net Benefits ($)', category_filter_sql:category_filter})
                
                if grouping_option != 'None':
                    plot_df = plot_df.rename(columns={reconstruct_column_name(grouping_option): grouping_option})
                
                categorical_summary_bar_fig = categorical_bar_fig(
                df = plot_df,
                col = 'final_dollar_value',
                category = category_filter,
                groupings = None if grouping_option == 'None' else grouping_option,
                figsize = (10, 6),
                single_bar_color = "darkgreen",
                space_fraction = 0.65,
                sort_by = None,
                sort_ascending = True,
                title = f"Benefits by {category_filter}",
                xlabel = '',
                ylabel = f"Net Benefits{categorical_bar_radio_options[grouping_option][1][0]}",
                y2label = None,
                legend = True,
                legend_loc = None,
                )

                st.pyplot(categorical_summary_bar_fig, clear_figure=True)

            with col2:
                st.markdown("##### Net Benefits Table")
                grouping_column = []
                if grouping_option != 'None':
                    grouping_column = [grouping_option]
                
                st.dataframe(
                    plot_df[[category_filter] + grouping_column + ['Net Benefits ($)']].query("`Net Benefits ($)` != 0"), 
                    width='stretch', 
                    hide_index=True,
                    column_config={
                        'Net Benefits ($)': st.column_config.NumberColumn(
                        label="Net Benefits ($)",
                        format="dollar",
                        )
                    }
                )
        
        st.divider()

        #Costs
        st.markdown("#### Costs")
        st.markdown("##### See Results by Impact Category and Value Stream")
        
        col1, col2 = st.columns(spec=[0.6, 0.4], gap="medium", border=False)
        
        with col1:
            costs_commoidty_results_df = con.execute(generate_costs_commodity_query(where_sql)).df()
            costs_commoidty_results_df, costs_commoidty_results_df_unit_labels = determine_dollar_magnitude(costs_commoidty_results_df, x_col='final_dollar_value', y_col=None)
            costs_commoidty_results_df['commodity'] = costs_commoidty_results_df['commodity'].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
            
            costs_bar_fig = numeric_bar_fig(
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
                ylabel = f'Costs{costs_commoidty_results_df_unit_labels[0]}',
                y2label = None,
                legend = False,
                legend_loc = None,
            )

            st.pyplot(costs_bar_fig, clear_figure=True)

        with col2:
            st.markdown("##### Costs Table")
            costs_value_stream_results_df = con.execute(generate_costs_value_stream_query(where_sql)).df()#.rename(columns={'final_dollar_value': 'Costs ($)'})
            costs_value_stream_results_df['Value Stream'] = costs_value_stream_results_df['Value Stream'].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
            st.dataframe(
                costs_value_stream_results_df, 
                width='stretch', 
                hide_index=True, 
                column_config={
                    'final_dollar_value': st.column_config.NumberColumn(
                        label="Costs ($)",
                        format="dollar",
                        )
                    }
                )

        st.divider()
        summary_results_df = con.execute(generate_summary_results_query()).df()
        st.markdown("### Summary Results Table:")
        st.dataframe(summary_results_df, width='stretch', hide_index=True)
        st.write(f"Using Database: `{db_value}`")
        