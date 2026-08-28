from typing import Any
import streamlit as st 
import os
import signal
from pathlib import Path
import duckdb
import pandas as pd
import numpy as np
import base64

from sql_queries import (
    generate_measure_filters_query,
    generate_jst_query, 
    generate_waterfall_query, 
    generate_benefit_cost_scatter_query,
    generate_benefits_impact_category_options_query, 
    generate_populated_temporal_cols_query, 
    generate_temporal_aggregation_benefits_query, 
    generate_null_aggregation_benefits_query, 
    generate_value_stream_benefits_query,
    generate_multiple_options_probe_query, 
    generate_categorical_summary_query,
    generate_costs_impact_category_query, 
    generate_costs_value_stream_query,
    generate_summary_results_query
)
from figures import (
    replace_multiple_string_elements,
    waterfall_multitier_fig, 
    numeric_bar_fig, 
    categorical_bar_fig,
    scatter_fig,
    pie_chart,
)
from helper_functions import (
    space_and_title,
    clean_column_name,
    reconstruct_column_name,
    determine_label_sig_figs, 
    determine_dollar_magnitude,
    determine_savings_magnitude,
    generate_all_row_combinations_df
)
from config.paths import (
    get_repo_root,
    get_input_templates_dir,
    get_output_dir,
    get_streamlit_app_dir,
    get_excel_input_parsing_project_dir,
    get_core_project_dir,
    # get_logos_dir,
    # get_logs_dir,
)
from config.env import setup_env_vars

st.set_page_config(layout="wide")

if 'show_value_streams_filter' not in st.session_state:
    st.session_state.show_value_streams_filter = None

if 'isolate_peak_filter' not in st.session_state:
    st.session_state.isolate_peak_filter = False

col1, col2, col3, col4, col5, col6 = st.columns([0.19, 0.05, 0.19, 0.19, 0.19, 0.19])

LOGOS_DIR = get_streamlit_app_dir() / "logos"
with col1:
    openbca_logo_path = LOGOS_DIR / "OpenBCA.jpg"
    openbca_logo_b64 = base64.b64encode(openbca_logo_path.read_bytes()).decode()
    st.markdown(
        f'[<img src="data:image/jpeg;base64,{openbca_logo_b64}" style="max-width:75%;height:auto;display:block;margin:0;margin-right:auto;"/>](https://www.naseo.org/topics/nesp/openbca)',
        unsafe_allow_html=True,
    )
with col3:
    lbnl_logo_path = LOGOS_DIR / "LBNL.jpg"
    lbnl_logo_b64 = base64.b64encode(lbnl_logo_path.read_bytes()).decode()
    st.markdown(
        f'[<img src="data:image/jpeg;base64,{lbnl_logo_b64}" style="max-width:38%;height:auto;display:block;margin:0;margin-right:auto;"/>](https://www.lbl.gov/)',
        unsafe_allow_html=True,
    )
with col4:
    naseo_logo_path = LOGOS_DIR / "NASEO.jpg"
    naseo_logo_b64 = base64.b64encode(naseo_logo_path.read_bytes()).decode()
    st.markdown(
        f'[<img src="data:image/jpeg;base64,{naseo_logo_b64}" style="max-width:57%;height:auto;display:block;margin-right:auto;"/>](https://naseo.org/)',
        unsafe_allow_html=True,
    )
with col5:
    icf_logo_path = LOGOS_DIR / "ICF.jpg"
    icf_logo_b64 = base64.b64encode(icf_logo_path.read_bytes()).decode()
    st.markdown(
        f'[<img src="data:image/jpeg;base64,{icf_logo_b64}" style="max-width:35%;height:auto;display:block;margin:0 auto;"/>](https://icf.com/)',
        unsafe_allow_html=True,
    )
with col6:
    recurve_logo_path = LOGOS_DIR / "RECURVE.jpg"
    recurve_logo_b64 = base64.b64encode(recurve_logo_path.read_bytes()).decode()
    st.markdown(
        f'[<img src="data:image/jpeg;base64,{recurve_logo_b64}" style="max-width:73%;height:auto;display:block;margin:0;margin-left:auto;"/>](https://recurve.com/)',
        unsafe_allow_html=True,
    )

# Resolve paths relative to this file, not the current working directory.
setup_env_vars()
REPO_ROOT = get_repo_root()
OUTPUT_DIR = get_output_dir()

# Match Makefile defaults (DB?=output/openbca.db, DBV?=output/openbca_input_validation.db) if not set.
DEFAULT_OUTPUT_DB = OUTPUT_DIR / "openbca.db"
DEFAULT_OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)

db_value = os.environ.get("DB", str(DEFAULT_OUTPUT_DB))
db_path = Path(db_value).expanduser()

title_col, quit_col = st.columns(spec=[0.88, 0.12], gap="small", border=False)
with title_col:
    st.markdown("## OpenBCA Insights and Analysis")
with quit_col:
    if st.button("Exit OpenBCA", type="primary"):
        print("Exiting Streamlit app...")
        # Get current pid and send SIGTERM to gracefully shut down the Streamlit server process
        os.kill(os.getpid(), signal.SIGTERM)

cost_impact_categories = ['Admin', 'Utility Incentive', 'Measure Cost', 'Tax Incentive']

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
        num_filters_excluding_id = len([f for f in filters if f != 'id'])

        where_sql = "WHERE 1=1"
        # Track explicit restrictions for the warning (not derived by parsing where_sql).
        active_filters = []
        # Full value sets (uncascaded) — used so cascaded option lists don't hide active filters.
        full_options_dict = {
            col: sorted(measure_filters_df[col].dropna().unique().tolist())
            for col in filters
        }
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
                    # Only cascade on explicit restrictions vs the full (uncascaded) value set.
                    if others_selection and set(others_selection) != set(full_options_dict[other]):
                        snippet = ", ".join(["'{}'".format(v) for v in others_selection])
                        sql += f" AND m.{other} IN ({snippet})"
                return sql

            filters_dict = {}
            filters_options_dict = {}
            with st.container(border=True):
                
                st.markdown("##### Universal Filters")
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
                            selection = st.multiselect(
                                label=f"Limit {space_and_title(category)} to:",
                                options=options,
                                default=default,
                                key=f"filter_{category}",
                            )
                            # Empty widget = no explicit restriction on this dimension.
                            if len(selection) == 0:
                                filters_dict[category] = options
                            else:
                                filters_dict[category] = selection
                                # Compare against full (uncascaded) options so mutually reinforcing
                                # filters stay in where_sql and in the active-filter warning.
                                if set(selection) != set(full_options_dict[category]):
                                    where_snippet = ", ".join(["'{}'".format(value) for value in selection])
                                    where_sql += f" AND m.{category} IN ({where_snippet})"
                                    active_filters.append(space_and_title(category))

        if active_filters:
            st.warning(f"Active filters: {', '.join(active_filters)}")

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

            
#############################   Portfolio Analysis   #####################################
               

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
                    help = f"When filters are selected will exclude program-level costs and benefits.",
                    index = 0, 
                    )

                max_waterfall_steps = 16
                waterfall_column = reconstruct_column_name(waterfall_filter)

                waterfall_results_initial_df = con.execute(generate_waterfall_query(where_sql, waterfall_column)).df().sort_values(by='final_dollar_value', key=abs, ascending=False)
                waterfall_results_total_df = pd.DataFrame([['total', waterfall_results_initial_df['final_dollar_value'].sum()]], columns=[waterfall_column, 'final_dollar_value'])
                
                waterfall_results_other_df = pd.DataFrame([], columns=[waterfall_column, 'final_dollar_value'])
                if len(waterfall_results_initial_df) > max_waterfall_steps:
                    waterfall_results_other_df = pd.DataFrame([['Other', waterfall_results_initial_df.tail(len(waterfall_results_initial_df) - max_waterfall_steps)['final_dollar_value'].sum()]], columns=[waterfall_column, 'final_dollar_value'])
                
                concat_parts = [
                    waterfall_results_initial_df.head(max_waterfall_steps),
                    waterfall_results_total_df
                ]

                if len(waterfall_results_other_df) > 0:
                    concat_parts.insert(1, waterfall_results_other_df)
                
                waterfall_results_df = pd.concat(concat_parts)
                
                waterfall_results_df['total'] = waterfall_results_df[waterfall_column].apply(lambda x: True if x == 'total' else False)
                waterfall_results_df[waterfall_column] = waterfall_results_df[waterfall_column].apply(lambda x: x.replace('_dollar', ''))
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
                        ylabel = f'Dollars {waterfall_unit_labels[0]}',
                        ylims = None,
                    )

                    st.pyplot(waterfall_fig, clear_figure=True)

                else:
                    waterfall_results_display_df = pd.concat([
                            waterfall_results_initial_df[[waterfall_column, 'final_dollar_value']],
                            waterfall_results_total_df[[waterfall_column, 'final_dollar_value']]
                        ])
                    
                    waterfall_results_display_df['total'] = waterfall_results_display_df[waterfall_column].apply(lambda x: True if x == 'total' else False)
                    
                    waterfall_results_display_df.sort_values(by=['total', 'final_dollar_value'], ascending=[True, False], inplace=True)
                    waterfall_results_display_df[waterfall_column] = waterfall_results_display_df[waterfall_column].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
                
                    st.dataframe(
                        waterfall_results_display_df[[waterfall_column, 'final_dollar_value']],
                        width='stretch', 
                        hide_index=True,
                        column_config={
                            waterfall_column: st.column_config.TextColumn(
                                label=space_and_title(waterfall_column),
                            ),
                            'final_dollar_value': st.column_config.NumberColumn(
                                label="Dollars ($)",
                                format="dollar",
                            )
                        }
                        )

            # Benefit and Cost Scatter Plot
            with col2:
                catalog_by_filter = ''
                if num_filters_excluding_id > 0: 
                    catalog_by_filter = st.radio(
                        "**Create Categories From**", 
                        options = [space_and_title(filter) for filter in filters if filter != 'id'], 
                        index = 0, 
                        horizontal = True,
                    )

                filter_col1, filter_col2 = st.columns(spec=[0.7, 0.3], gap="small", border=False)
                
                with filter_col1:
                    benefits_vs_costs_or_jst_ratio = st.segmented_control(
                        label = "**Plot**", 
                        options = ['Benefits vs Costs', 'JST Ratio vs Net Benefits'], 
                        default='Benefits vs Costs',
                        key = "benefits_vs_costs_or_jst"
                        ) 

                with filter_col2:
                    show_id_labels = st.checkbox(
                            label = "**Show ID Labels**",
                            value = False,
                            key = "show_id_labels",
                        )

                if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs':
                    scatter_x_col = 'total_costs'
                    scatter_y_col = 'total_benefits'
                elif benefits_vs_costs_or_jst_ratio == 'JST Ratio vs Net Benefits':
                    scatter_x_col = 'net_benefits'
                    scatter_y_col = 'jst_ratio'

                benefit_cost_scatter_df = con.execute(generate_benefit_cost_scatter_query(where_sql, reconstruct_column_name(catalog_by_filter))).df()
                if num_filters_excluding_id > 0:
                    cat_col = reconstruct_column_name(catalog_by_filter)
                    benefit_cost_scatter_df[cat_col] = benefit_cost_scatter_df[cat_col].fillna("None")

                benefit_cost_scatter_df, benefit_cost_scatter_unit_labels, benefit_cost_scatter_scale_exponent = determine_dollar_magnitude(
                    benefit_cost_scatter_df, 
                        x_col=scatter_x_col, 
                        y_col=scatter_y_col,
                        return_scale_exponent=True
                        )

                if waterfall_scatter_fig_or_table == 'Figures':       

                    padding = 0.08    
                    min_x_scatter_val = min(0, benefit_cost_scatter_df[scatter_x_col].min())     
                    max_x_scatter_val = max(0, benefit_cost_scatter_df[scatter_x_col].max())
                    min_y_scatter_val = min(0, benefit_cost_scatter_df[scatter_y_col].min())
                    max_y_scatter_val = max(0, benefit_cost_scatter_df[scatter_y_col].max())

                    x_scatter_range = max_x_scatter_val - min_x_scatter_val
                    y_scatter_range = max_y_scatter_val - min_y_scatter_val
                    
                    x_scatter_min = min_x_scatter_val - padding * x_scatter_range
                    x_scatter_max = max_x_scatter_val + padding * x_scatter_range
                    y_scatter_min = min_y_scatter_val - padding * y_scatter_range
                    y_scatter_max = max_y_scatter_val + padding * y_scatter_range                    

                    min_scatter_val = benefit_cost_scatter_df[[scatter_x_col, scatter_y_col]].min().min()
                    max_scatter_val = benefit_cost_scatter_df[[scatter_x_col, scatter_y_col]].max().max()
                    scatter_range = max_scatter_val - min_scatter_val
                    axis_min = min_scatter_val - padding * scatter_range
                    axis_max = max_scatter_val + padding * scatter_range

                    # Dynamic marker size based on number of data points
                    min_marker_size = 100
                    max_marker_size = 300 
                    marker_size = max(min_marker_size, min(max_marker_size, min_marker_size + 10*(max_marker_size - min_marker_size) / len(benefit_cost_scatter_df)))

                    def _numeric_string_labeling(value: str):
                        try:
                            v = float(value)
                            if v.is_integer():
                                return int(v)
                            else:
                                return v
                        except:
                            return value

                    label_list =[str(value) for value in sorted([_numeric_string_labeling(value) for value in benefit_cost_scatter_df[f"{reconstruct_column_name(catalog_by_filter)}"].unique()])] if len(catalog_by_filter) > 0 else None

                    benefit_cost_scatter_fig = scatter_fig(
                        df = benefit_cost_scatter_df,
                        xy_cols_dict = {
                            scatter_x_col:{'uncertainty_col':None, 'label': f'{scatter_x_col} ($)'},
                            scatter_y_col:{'uncertainty_col':None, 'label': f'{scatter_y_col} ($)'}
                            },
                        marker_size = marker_size,
                        include_45_degree_line = True if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else False,
                        hline_y_position = 0 if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else 1,
                        color_by_col = None if len(catalog_by_filter) == 0 else reconstruct_column_name(catalog_by_filter),
                        label_points = True if show_id_labels else False,
                        labels = benefit_cost_scatter_df['id'].tolist(),
                        label_size = 10,
                        figsize = (8, 6),
                        title = f"{space_and_title(benefits_vs_costs_or_jst_ratio)}{' by ' if len(catalog_by_filter) > 0 else ''}{catalog_by_filter}",
                        xlims = [axis_min, axis_max] if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else [x_scatter_min, x_scatter_max],
                        xlabel = f"{'Costs' if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else 'Net Benefits'} {benefit_cost_scatter_unit_labels[0]}",
                        ylims = [axis_min, axis_max] if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else [y_scatter_min, y_scatter_max],
                        ylabel = f"{'Benefits' if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else 'JST Ratio'} {benefit_cost_scatter_unit_labels[1] if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else ''}",
                        legend = True,
                        legend_labels = None if len(catalog_by_filter) == 0 else sorted(list(benefit_cost_scatter_df[f"{reconstruct_column_name(catalog_by_filter)}"].unique())),
                        legend_loc = 'best' 
                    )

                    st.pyplot(benefit_cost_scatter_fig, clear_figure=True)

                else:
                    sort_col = 'id'
                    if len(catalog_by_filter) > 0:
                        sort_col = reconstruct_column_name(catalog_by_filter)

                    benefit_cost_scatter_df.sort_values(by=[sort_col, 'total_benefits'], ascending=[True, False], inplace=True)
                    benefit_cost_scatter_df[sort_col] = benefit_cost_scatter_df[sort_col].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))

                    st.dataframe(
                        benefit_cost_scatter_df[list(set([
                            'id', sort_col, 'total_costs', 'total_benefits', 'net_benefits', 'jst_ratio'
                            ]))].sort_values(
                                by='net_benefits' if benefits_vs_costs_or_jst_ratio == 'Benefits vs Costs' else 'jst_ratio', ascending=False), 
                        width='stretch', 
                        hide_index=True,
                        column_config={
                            sort_col: st.column_config.TextColumn(
                                label=space_and_title(sort_col),
                            ),
                            'total_costs': st.column_config.NumberColumn(
                                label="Costs ($)",
                                format="dollar",
                            ),
                            'total_benefits': st.column_config.NumberColumn(
                                label="Benefits ($)",
                                format="dollar",
                            ),
                            'net_benefits': st.column_config.NumberColumn(
                                label="Net Benefits ($)",
                                format="dollar",
                            ),
                            'jst_ratio': st.column_config.NumberColumn(
                                label="JST Ratio",
                                format="%.2f",
                            )
                        }
                    )

            st.divider()


#############################   Benefits Analysis   #####################################


            header_col1, header_col2 = st.columns(spec=[0.55, 0.45], gap="medium", border=False)
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

            benefits_impact_category_options_df = con.execute(generate_benefits_impact_category_options_query(where_sql)).df()
            benefits_impact_category_options = [space_and_title(impact_category) for impact_category in benefits_impact_category_options_df['impact_category'].tolist()]

            impact_category_filter = st.radio(
                label = "**Impact Category**", 
                options = benefits_impact_category_options, 
                horizontal = True,
                index = 0 if 'Electric' not in benefits_impact_category_options else benefits_impact_category_options.index('Electric'), 
                )

            if impact_category_filter == 'Electric':
                unit = 'kWh'
            elif impact_category_filter in ['Natural Gas', 'Propane', 'Oil', 'Diesel', 'Wood']:
                unit = 'MMBtu'
            else:
                unit = ''
            
            temporal_cols = ['hour_of_day', 'month', 'year']
            impact_category_filter = impact_category_filter.upper()

            populated_temporal_cols = []
            for col in temporal_cols:
                if len(
                    con.execute(generate_populated_temporal_cols_query(where_sql, impact_category_filter, col)).df()
                ) > 0:
                    populated_temporal_cols.append(col)

            temporal_aggregation_filter = 'year'

            col1, col2 = st.columns(spec=[0.58, 0.42], gap="medium", border=False)

            # Benefits  

            with col1:  

                if len(populated_temporal_cols) > 1:
                    subcol1, subcol2, subcol3 = st.columns(spec=[0.46, 0.53, 0.01], gap="small", border=False)

                    temporal_aggregation_filter = subcol1.radio(
                        label = "**Aggregation**",
                        options = [space_and_title(col) for col in populated_temporal_cols],
                        index = 0,
                        horizontal = True,
                        )

                    temporal_aggregation_filter = reconstruct_column_name(temporal_aggregation_filter)
                        
                    null_aggregation_benefits_df = con.execute(generate_null_aggregation_benefits_query(where_sql, impact_category_filter, temporal_aggregation_filter)).df()
                    lower_granularity_value_streams = null_aggregation_benefits_df.query("value_stream != 'total'")['value_stream'].tolist()
                    if len(null_aggregation_benefits_df) > 0:
                        null_aggregation_benefits = null_aggregation_benefits_df.query("value_stream == 'total'")['final_dollar_value'].values[0]
                        subcol2.write(f"")
                        with subcol2.container(border=True):
                            st.markdown(f"###### Lower granularity benefits = **${null_aggregation_benefits:,.0f}**", help=f"Benefits that accrue from value streams with lower temporal granularity than displayed in the figure. For example, if monthly benefits are shown, then value streams that can only be quantified at an annual level are accounted for here. In the current selection, these value streams include: {', '.join(lower_granularity_value_streams)}.")

                # Use widget key "isolate_peak" for current value (updated at run start); fallback to isolate_peak_filter
                isolate_peak_active = (
                    impact_category_filter.upper() == 'ELECTRIC'
                    and temporal_aggregation_filter == 'hour_of_day'
                    and st.session_state.get("isolate_peak", st.session_state.isolate_peak_filter)
                )

                # Reset peak filters when they don't apply
                if not (impact_category_filter.upper() == 'ELECTRIC' and temporal_aggregation_filter == 'hour_of_day'):
                    st.session_state.isolate_peak_filter = False
                    if "isolate_peak" in st.session_state:
                        st.session_state["isolate_peak"] = False
                    st.session_state["peak_months_filter"] = []
                    st.session_state["peak_hours_filter"] = []
                elif not isolate_peak_active:
                    # User turned off "Isolate Peak Period" or not in peak context — clear month/hour selections
                    st.session_state["peak_months_filter"] = []
                    st.session_state["peak_hours_filter"] = []

                filtercol1, filtercol2 = st.columns(spec=[0.5, 0.5], gap="medium", border=False)

                temporal_aggregation_results_df = con.execute(
                    generate_temporal_aggregation_benefits_query(
                        where_sql, 
                        impact_category_filter, 
                        temporal_aggregation_filter, 
                        peak_months=st.session_state.get("peak_months_filter", []) if isolate_peak_active else [], 
                        group_by_value_stream=False
                    )
                ).df().query(f"~{temporal_aggregation_filter}.isna()")

                temporal_aggregation_results_df, temporal_aggregation_results_unit_labels, temporal_aggregation_results_scale_exponent = determine_dollar_magnitude(temporal_aggregation_results_df, x_col='final_dollar_value', return_scale_exponent=True)
                temporal_aggregation_results_df, temporal_aggregation_results_savings_unit_labels = determine_savings_magnitude(temporal_aggregation_results_df, x_col='net_lifecycle_energy_savings', unit=unit)
                
                temporal_aggregation_value_stream_results_df = con.execute(
                    generate_temporal_aggregation_benefits_query(
                        where_sql, 
                        impact_category_filter, 
                        temporal_aggregation_filter, 
                        peak_months=st.session_state.get("peak_months_filter", []) if isolate_peak_active else [], 
                        group_by_value_stream=True
                    )
                ).df().query(f"~{temporal_aggregation_filter}.isna()")

                temporal_aggregation_value_stream_results_df['final_dollar_value_original'] = temporal_aggregation_value_stream_results_df['final_dollar_value']
                temporal_aggregation_value_stream_results_df['final_dollar_value'] = temporal_aggregation_value_stream_results_df['final_dollar_value'] / 10**(temporal_aggregation_results_scale_exponent)
                temporal_aggregation_value_stream_results_df['value_stream'] = temporal_aggregation_value_stream_results_df['value_stream'].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))

                value_streams = sorted([v for v in temporal_aggregation_value_stream_results_df['value_stream'].unique().tolist() if 'GHG Intensity' not in v])
                value_streams_filter = []
                if len(value_streams) > 0:
                    value_streams_filter = st.session_state.get("value_streams_filter", [])

                if impact_category_filter.upper() == 'ELECTRIC' and temporal_aggregation_filter == 'hour_of_day':
                    st.session_state.isolate_peak_filter = st.checkbox(
                        label = f"**Isolate Peak Period**",
                        value = False,
                        key = "isolate_peak",
                    )
                
                if isolate_peak_active:
                    with st.container(border=True):
                        peakfiltercol1, peakfiltercol2 = st.columns(spec=[0.5, 0.5], gap="medium", border=False)
                    
                        with peakfiltercol1:
                                
                            st.multiselect(
                                label = f"**Define Peak Months:**",
                                options = range(1, 13),
                                key = "peak_months_filter",
                                default = []
                            )

                        with peakfiltercol2:

                            st.multiselect(
                                label = f"**Define Peak Hours:**",
                                options = range(0, 24),
                                key = "peak_hours_filter",
                                default = []
                            )

                if bar_pie_fig_or_table == 'Figures':
                    temporal_aggregation_bar_fig = numeric_bar_fig(
                        df = temporal_aggregation_results_df,
                        col = 'final_dollar_value',
                        category = temporal_aggregation_filter,
                        value_stream_df = temporal_aggregation_value_stream_results_df.query(f"value_stream in {value_streams_filter}") if len(value_streams_filter) > 0 else None,
                        figsize= (10, 6),
                        y2_col = 'net_lifecycle_energy_savings' if len(temporal_aggregation_results_df.query("~net_lifecycle_energy_savings.isna()")) > 0 else None,
                        pin_yaxis_zeros = True,
                        single_bar_color="cornflowerblue",
                        space_fraction = 0.65,
                        peak_period = st.session_state.get('peak_hours_filter', []),# if isolate_peak_active else None,
                        title = f"Benefits by {space_and_title(temporal_aggregation_filter)}",
                        xlabel = None,
                        ylabel = f'Benefits{temporal_aggregation_results_unit_labels[0]}',
                        y2label = f'Savings {temporal_aggregation_results_savings_unit_labels[0]}', 
                        legend = True if len(value_streams_filter) > 0 else False, 
                        legend_loc = 'best',
                    )

                    st.pyplot(temporal_aggregation_bar_fig, clear_figure=True)

                    if len(value_streams) > 0:
                        st.multiselect(
                            label = f"**Show Specific Value Streams:**",
                            options = value_streams,
                            key = "value_streams_filter",
                            default = []
                        )   

                else:
                    savings_label = ''
                    if impact_category_filter.upper() == 'ELECTRIC':
                        savings_label = ' (kWh)'
                    elif impact_category_filter.upper() in ['NATURAL GAS', 'PROPANE', 'OIL', 'DIESEL', 'WOOD']:
                        savings_label = ' (MMBtu)'

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
                        label=f'Savings{savings_label}',
                        format="%.2f",
                        )},
                    )
        
            with col2:

                def pie_fig_section( 
                    isolate_peak: bool = False,
                    peak_months: list[int] = [],
                    peak_hours: list[int] = [],
                ):
                    st.write(f"")
                    value_stream_benefits_df = con.execute(generate_value_stream_benefits_query(where_sql, impact_category_filter, peak_months=peak_months, peak_hours=peak_hours)).df()
                    value_stream_benefits_df['value_stream'] = value_stream_benefits_df['value_stream'].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
                    pos_value_stream_benefits_df = value_stream_benefits_df.query("final_dollar_value > 0")
                    neg_value_stream_benefits_df = value_stream_benefits_df.query("final_dollar_value < 0")
                    st.markdown(f"##### {'Peak ' if isolate_peak else 'Total '}{space_and_title(impact_category_filter)} Benefit Value Streams (${value_stream_benefits_df['final_dollar_value'].sum():,.0f})")

                    if len(value_stream_benefits_df) == 1:
                        value_stream_benefits = value_stream_benefits_df['final_dollar_value'].values[0]

                        for i in range(6):
                            st.write(f"")
                        
                        st.markdown(f"#### {space_and_title(impact_category_filter)} Benefits = **${value_stream_benefits:,.0f}**")

                    else:
                        if bar_pie_fig_or_table == 'Figures':
                            pos_value_stream_benefits_unit_labels = ['']
                            neg_value_stream_benefits_unit_labels = ['']

                            if len(pos_value_stream_benefits_df) > 0:
                                pos_value_stream_benefits_df, pos_value_stream_benefits_unit_labels = determine_dollar_magnitude(pos_value_stream_benefits_df, x_col='final_dollar_value', y_col=None)
                            
                            if len(neg_value_stream_benefits_df) > 0:
                                neg_value_stream_benefits_df, neg_value_stream_benefits_unit_labels = determine_dollar_magnitude(neg_value_stream_benefits_df, x_col='final_dollar_value', y_col=None)

                            pie_chart_fig = pie_chart(
                                df = pos_value_stream_benefits_df if len(pos_value_stream_benefits_df) > 0 else neg_value_stream_benefits_df,
                                col = 'final_dollar_value',
                                label_col = 'value_stream',
                                figsize = (9, 5),
                                title = f"{space_and_title(impact_category_filter)} Benefits{pos_value_stream_benefits_unit_labels[0] if len(pos_value_stream_benefits_df) > 0 else neg_value_stream_benefits_unit_labels[0]}"
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
                                
                    return

                if isolate_peak_active and (len(st.session_state.get("peak_months_filter", [])) > 0 or len(st.session_state.get("peak_hours_filter", [])) > 0):
                    pie_fig_section(isolate_peak=True, peak_months=st.session_state.get("peak_months_filter", []), peak_hours=st.session_state.get("peak_hours_filter", []))
                    st.divider()
                pie_fig_section(isolate_peak=False, peak_months=[], peak_hours=[])


#############################   Comparative Analysis   #####################################


        category_filters = con.execute(
            generate_multiple_options_probe_query(
                where_sql, column_names=[filter for filter in filters if filter != 'id']+['impact_category']
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

                net_benefits_or_jst_ratio = st.segmented_control(
                    label = "**Plot**", 
                    options = ['Net Benefits', 'JST Ratio'], 
                    default='Net Benefits',
                    key = "net_benefits_or_jst"
                    ) 

                bar_col = 'final_dollar_value'
                if net_benefits_or_jst_ratio == 'JST Ratio':
                    bar_col = 'jst_ratio'

                category_filter_sql = f"{reconstruct_column_name(category_filter)}"

                categorical_summary_df = con.execute(generate_categorical_summary_query(where_sql, category_filter_sql, include_costs = True)).df().query(f"not {category_filter_sql}.isnull()")
                categorical_summary_df, categorical_summary_unit_labels = determine_dollar_magnitude(categorical_summary_df, x_col=bar_col, y_col=None)        
                categorical_summary_df[f"{category_filter_sql}"] = categorical_summary_df[f"{category_filter_sql}"].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
                
                remaining_category_filters = [filter for filter in category_filters if filter != category_filter_sql]

                categorical_bar_radio_options = {'None': [categorical_summary_df, categorical_summary_unit_labels]}

            with col2:    
                for grouping_filter in remaining_category_filters:

                    categorical_grouping_summary_df = con.execute(generate_categorical_summary_query(where_sql, category_filter_sql, grouping_filter = grouping_filter, include_costs = True)).df().query(f"not {grouping_filter}.isnull()")
                    if len(categorical_grouping_summary_df) > len(categorical_summary_df):
                        categorical_grouping_summary_df, categorical_grouping_summary_unit_labels = determine_dollar_magnitude(categorical_grouping_summary_df, x_col=bar_col, y_col=None)
                        categorical_grouping_summary_df[f"{grouping_filter}"] = categorical_grouping_summary_df[f"{grouping_filter}"].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
                        categorical_bar_radio_options[space_and_title(grouping_filter)] = [categorical_grouping_summary_df, categorical_grouping_summary_unit_labels]
                
                grouping_option = 'None'        
                if len(categorical_bar_radio_options.keys()) > 1:
                    grouping_option = st.radio(
                        label = "**Break Out Results By**",
                        options = [c for c in categorical_bar_radio_options.keys() if c != 'Impact Category'],
                        index = 0,
                        horizontal = True,
                    )

            col1, col2 = st.columns(spec=[0.6, 0.4], gap="medium", border=False)

            with col1:
                plot_df = generate_all_row_combinations_df(
                    df=categorical_bar_radio_options[grouping_option][0], 
                    col_1=category_filter_sql, 
                    col_2=reconstruct_column_name(grouping_option), 
                    numeric_cols=[bar_col, bar_col+'_original']+[col for col in ['jst_ratio', 'final_dollar_value'] if col != bar_col]
                    ).rename(columns={category_filter_sql:category_filter})

                if grouping_option != 'None':
                    plot_df = plot_df.rename(columns={reconstruct_column_name(grouping_option): grouping_option})

                categorical_summary_bar_fig = categorical_bar_fig(
                df = plot_df[~plot_df[category_filter].isin(cost_impact_categories)],
                col = bar_col,
                category = category_filter,
                groupings = None if grouping_option == 'None' else grouping_option,
                figsize = (10, 6),
                #single_bar_color = "darkolivegreen",
                space_fraction = 0.65,
                sort_by = None,
                sort_ascending = True,
                title = f"Benefits by {category_filter}",
                xlabel = '',
                ylabel = f"{'Net Benefits' if net_benefits_or_jst_ratio == 'Net Benefits' else 'JST Ratio'}{categorical_summary_unit_labels[0] if net_benefits_or_jst_ratio == 'Net Benefits' else ''}",
                y2label = None,
                legend = True,
                legend_loc = 'best',
                )

                st.pyplot(categorical_summary_bar_fig, clear_figure=True)

            with col2:
                st.markdown("##### Net Benefits Table")
                grouping_column = []
                if grouping_option != 'None':
                    grouping_column = [grouping_option]

                if 'final_dollar_value_original' not in plot_df.columns:
                    plot_df['final_dollar_value_original'] = plot_df['final_dollar_value'] 
                
                st.dataframe(
                    plot_df[~plot_df[category_filter].isin(cost_impact_categories)][[category_filter] + grouping_column + ['final_dollar_value_original', 'jst_ratio']].query("final_dollar_value_original != 0"), 
                    width='stretch', 
                    hide_index=True,
                    column_config={
                        'final_dollar_value_original': st.column_config.NumberColumn(
                        label="Net Benefits ($)",
                        format="dollar",
                        ),
                        'jst_ratio': st.column_config.NumberColumn(
                        label="JST Ratio",
                        format="%.2f",
                        ),
                    }
                )
        
        st.divider()


#############################   Costs Analysis   #####################################


        st.markdown("#### Costs")
        st.markdown("##### See Results by Impact Category and Value Stream")
        
        col1, col2 = st.columns(spec=[0.6, 0.4], gap="medium", border=False)
        
        with col1:
            costs_commoidty_results_df = con.execute(generate_costs_impact_category_query(where_sql)).df()
            costs_commoidty_results_df, costs_commoidty_results_df_unit_labels = determine_dollar_magnitude(costs_commoidty_results_df, x_col='final_dollar_value', y_col=None)
            costs_commoidty_results_df['impact_category'] = costs_commoidty_results_df['impact_category'].apply(lambda x: replace_multiple_string_elements(space_and_title(x)))
            
            costs_bar_fig = numeric_bar_fig(
                df = costs_commoidty_results_df,
                col = 'final_dollar_value',
                category = 'impact_category',
                figsize= (9, 5),
                pin_yaxis_zeros = True,
                single_bar_color="indianred",
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
        summary_results_df.columns = [clean_column_name(col) for col in summary_results_df.columns]
        st.markdown("### Summary Results Table:")
        st.dataframe(summary_results_df, width='stretch', hide_index=True)
        
        st.write(f"Using Database: `{db_value}`")