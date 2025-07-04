import altair as alt
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

from app_data import *

st.set_page_config(layout="wide")

PROJECT_ID = get_script_run_ctx().session_id

# hide header
st.markdown("""<style> .block-container {padding-top: 1rem;} header[data-testid="stHeader"] {height: 0px;visibility: hidden;} </style>""", unsafe_allow_html=True)

st.markdown("# OpenBCA")

def impact_selection(commodity: str):
    value_streams_df = get_value_streams()
    value_streams_df = value_streams_df[value_streams_df['commodity'] == commodity]
    options = sorted(value_streams_df['avoided_cost'].unique().tolist())  # sorted = stable order

    widget_key = f"{commodity}_multiselect"
    selected = st.multiselect(
        f"Select value streams for {commodity}",
        options,
        default=options,
        key=widget_key,
    )

    return selected

main_cols = st.columns([2, 3])

with main_cols[0]:

    with st.expander("Inputs", expanded=True):
        filter_rows = st.columns(4)

        with filter_rows[0]:
            avoided_cost_subset = st.selectbox("Subset", get_avoided_cost_subsets())

        with filter_rows[1]:
            start_year = st.number_input("Start Year", value=2021, step=1)
            start_quarter = st.selectbox("Start Quarter", [1, 2, 3, 4])

        with filter_rows[2]:
            eul = st.number_input("EUL", value=10)
            discount_rate = st.number_input("Discount Rate", value=0.075)

        with filter_rows[3]:
            units = st.number_input("Units", value=1, step=1)
            ntg = st.number_input("NTG", value=1.0, step=0.01)

        costs_col = st.columns(3)
        with costs_col[0]:
            admin_cost = st.number_input("Administrative Cost", value=3000)
        with costs_col[1]:
            incentive_cost = st.number_input("Incentive Cost", value=500)
        with costs_col[2]:
            measure_cost = st.number_input("Measure Cost", value=1000)

        commodity_input_tabs = st.tabs(["Electricity", "Gas"])

        with commodity_input_tabs[0]:
            elec_commodity_cols = st.columns(2)
            with elec_commodity_cols[0]:
                electric_curve = st.selectbox("Electric Value Curve", get_electricity_value_curves())
            with elec_commodity_cols[1]:
                mwh_savings = st.number_input("Annual MWh saving", value=10)

            electricity_impact_selection = impact_selection('ELECTRICITY')

        with commodity_input_tabs[1]:
            gas_commodity_cols = st.columns(2)
            with gas_commodity_cols[0]:
                gas_curve = st.selectbox("Gas Value Curve", get_gas_value_curves())
            with gas_commodity_cols[1]:
                therms_savings = st.number_input("Annual Therms saving", value=100)

            gas_impact_selection = impact_selection('GAS')

        update_project(
            PROJECT_ID,
            avoided_cost_subset=avoided_cost_subset,
            start_year=start_year, start_quarter=start_quarter,
            discount_rate=discount_rate, eul=eul,
            units=units, ntg=ntg,
            mwh_savings=mwh_savings, load_shape=electric_curve,
            therms_savings=therms_savings, therms_profile=gas_curve,
            admin_cost=admin_cost, incentive_cost=incentive_cost, measure_cost=measure_cost,
        )

with main_cols[1]:

    def f_n(value: float) -> str:
        return f"{value:,.0f}"

    def render_metric(name: str, value: str, electric_value: str = None, gas_value: str = None):
        details = f"<small>Electric: {electric_value} | Gas: {gas_value}</small>" if electric_value or gas_value else ""
        st.markdown(f"""
            <div style='padding: 10px; border: 1px solid #ccc; border-radius: 10px;'>
                <strong>{name}</strong><br>
                <span style='font-size: 24px;'>{value}</span><br>
                {details}
            </div>
        """, unsafe_allow_html=True)


    result = get_project_impacts(PROJECT_ID, electricity_impact_selection, gas_impact_selection)

    with st.container():
        row_top = st.columns(2)
        with row_top[0]:
            render_metric("Net Lifecycle MWh Savings", f"{result[PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS]:,.0f}")
        with row_top[1]:
            render_metric("Net Lifecycle Therm Savings", f"{result[PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS]:,.0f}")

        st.markdown(" ")
        row_mid = st.columns([2, 1.5, 2, 1, 1])

        with row_mid[0]:
            render_metric(
                "Total System Benefit", f"{result[PROJECT_IMPACT_TOTAL_BENEFITS]:,.0f}",
                f"{result[PROJECT_IMPACT_ELECTRIC_BENEFITS]:,.0f}",
                f"{result[PROJECT_IMPACT_GAS_BENEFITS]:,.0f}"
            )
        with row_mid[1]:
            st.markdown(f"""<div style='padding: 10px; border: 1px solid #ccc; border-radius: 10px;'>
                <strong>TSB/MWh</strong><br><span style='font-size: 24px;'>{f"{result[PROJECT_IMPACT_TOTAL_BENEFITS_PER_MWH]:,.2f}"}</span><br>
                <small>TSB/Therm {f"{result[PROJECT_IMPACT_TOTAL_BENEFITS_PER_THERM]:,.2f}"}</small>
            </div>""", unsafe_allow_html=True)
        # with row_mid[2]: FIXME reactivate
        #     render_metric(
        #         "GHG Savings (Tons)", f"{result[PROJECT_IMPACT_TOTAL_GHG_BENEFITS]:,.0f}",
        #         f"{result[PROJECT_IMPACT_ELECTRIC_GHG_BENEFITS]:,.0f}",
        #         f"{result[PROJECT_IMPACT_GAS_GHG_BENEFITS]:,.0f}"
        #     )
        with row_mid[3]:
            render_metric("TRC", f"{result[PROJECT_IMPACT_TRC_RATIO]:,.2f}")
        with row_mid[4]:
            render_metric("PAC", f"{result[PROJECT_IMPACT_PAC_RATIO]:,.2f}")

    energy_tabs = st.tabs(["Electricity", "Gas"])

    with energy_tabs[0]:
        electric_chart_data = get_electricity_impacts_by_avoided_cost_ts(PROJECT_ID, electricity_impact_selection)
        electric_chart = alt.Chart(electric_chart_data).mark_bar().encode(
            x=alt.X("Hour of Day:O", title="Hour of Day"),
            y=alt.Y("sum($ / MWh):Q", title="$ / MWh"),
            color=alt.Color("Category:N", legend=alt.Legend(title="$ / MWh"))
        ).properties(title="Hourly Electricity Costs by Category")
        st.altair_chart(electric_chart, use_container_width=True)

    with energy_tabs[1]:
        gas_chart_data = get_gas_impacts_by_avoided_cost_ts(PROJECT_ID, gas_impact_selection)
        gas_chart = alt.Chart(gas_chart_data).mark_bar().encode(
            x="Month:O", y="$ / Therm:Q", color="Component:N"
        ).properties(title="Monthly Gas Costs by Component")
        st.altair_chart(gas_chart, use_container_width=True)
