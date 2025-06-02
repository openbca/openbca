import altair as alt

from app_data import *

st.set_page_config(layout="wide")

st.markdown("# OpenBCA")

with st.expander("Inputs", expanded=True):
    filter_rows = st.columns(4)

    with filter_rows[0]:
        st.markdown("#### Value Curve")
        electric_curve = st.selectbox("Electric Value Curve", ["NONRES_INDOOR_CFL_LTG", "NONRES_HVAC_SPLIT_PACKAGE_AC"])
        gas_curve = st.selectbox("Gas Value Curve", ["annual"])

    with filter_rows[1]:
        st.markdown("#### Utility & Zone")
        utility = st.selectbox("Utility", ["PGE"])
        climate_zone = st.selectbox("Climate Zone", ['CZ12', 'CZ2', 'CZ3A', 'CZ3B', 'CZ12'])

    with filter_rows[2]:
        st.markdown("#### Time Period")
        start_year = st.number_input("Start Year", value=2021, step=1)
        start_quarter = st.selectbox("Start Quarter", [1, 2, 3, 4])

    with filter_rows[3]:
        st.markdown("#### Financial Inputs")
        eul = st.number_input("EUL", value=10)
        discount_rate = st.number_input("Discount Rate", value=0.075)

    st.markdown("#### Impacts Selection")
    selected_streams = []
    value_streams = load_value_streams()
    stream_cols = st.columns(len(value_streams))
    for i, (stream, color) in enumerate(value_streams.items()):
        with stream_cols[i]:
            checked = st.checkbox(f"{stream}", value=True)
            if checked:
                selected_streams.append(stream)
            st.markdown(f"<div style='height:10px;width:100%;background-color:{color};margin-top:5px;border-radius:2px'></div>", unsafe_allow_html=True)

    # INPUT_PROJECT_FIELDS = ['utility', 'region', 'start_year', 'start_quarter', 'discount_rate', 'eul', 'units', 'ntg',
    #                         'admin_cost', 'incentive_cost', 'measure_cost', 'mwh_savings', 'therms_savings',
    #                         'load_shape', 'therms_profile']

    refresh_project_table(
        utility=utility,
        region=climate_zone,
        start_year=start_year,
        start_quarter=start_quarter,
        discount_rate=discount_rate,
        eul=eul,
        units=1,
        ntg=1,
        admin_cost=1,
        incentive_cost=1,
        measure_cost=1,
        mwh_savings=1,
        therms_savings=1,
        load_shape=electric_curve,
        therms_profile=gas_curve,
    )

st.markdown("## Total System Benefits")

def render_metric(name: str, value: float, details: str = ""):
    st.markdown(f"""
            <div style='padding: 10px; border: 1px solid #ccc; border-radius: 10px;'>
                <strong>{name}</strong><br>
                <span style='font-size: 24px;'>{value}</span><br>
                {details}
            </div>
        """, unsafe_allow_html=True)

result = load_calculation_results()

with st.container():
    row_top = st.columns(2)
    with row_top[0]:
        render_metric("Net Lifecycle MWh Savings", result[PROJECT_IMPACT_ELECTRIC_BENEFITS])
    with row_top[1]:
        render_metric("Net Lifecycle Therm Savings", result[PROJECT_IMPACT_GAS_BENEFITS])

    st.markdown("### System Benefits and Savings")
    row_mid = st.columns([2, 1.5, 2, 1, 1])

    with row_mid[0]:
        render_metric("Total System Benefit", result[PROJECT_IMPACT_TOTAL_BENEFITS], "<small>Electric: 8,082 | Gas: 1,501</small>")
    with row_mid[1]:
        render_metric("TSB/MWh", 5000, "<small>TSB/Therm: 1.50</small>")
    with row_mid[2]:
        render_metric("GHG Savings (Tons)", result[PROJECT_IMPACT_LIFECYCLE_TOTAL_GHG_SAVINGS], "<small>Electric: 27.37 | Gas: 5.29</small>")
    with row_mid[3]:
        render_metric("TRC", result[PROJECT_IMPACT_TRC_RATIO])
    with row_mid[4]:
        render_metric("PAC", result[PROJECT_IMPACT_PAC_RATIO])

# Tabs for Electricity and Gas
energy_tabs = st.tabs(["Electricity", "Gas"])


with energy_tabs[0]:
    st.markdown("## Electricity")
    electric_cols = st.columns(4)
    electric_cols[0].metric("$/MWh", "67.50")
    electric_cols[1].metric("Peak $/MWh", "368.89")
    electric_cols[2].metric("Off Peak $/MWh", "44.94")
    electric_cols[3].metric("Marginal GHG Tons/MWh", "0.32")

    electric_chart_data = load_electric_chart_data()
    electric_chart = alt.Chart(electric_chart_data).mark_bar().encode(
        x=alt.X("Hour of Day:O", title="Hour of Day"),
        y=alt.Y("sum($ / MWh):Q", title="$ / MWh"),
        color=alt.Color("Category:N", legend=alt.Legend(title="$ / MWh"))
    ).properties(title="Hourly Electricity Costs by Category")
    st.altair_chart(electric_chart, use_container_width=True)
    peak_offpeak_df = load_peak_offpeak()
    line_chart = alt.Chart(peak_offpeak_df).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("$ / MWh:Q", title="$ / MWh"),
        color=alt.Color("Type:N", scale=alt.Scale(domain=["peak", "off_peak"], range=["blue", "red"])),
        strokeDash="Type"
    ).properties(title="Peak Period = June - Sept, 4 - 9 pm     *Discount Rate Applied")
    st.altair_chart(line_chart, use_container_width=True)

    electric_table = load_electric_table()
    st.dataframe(electric_table)


with energy_tabs[1]:
    st.markdown("## Gas")
    gas_cols = st.columns(4)
    gas_cols[0].metric("$/Therm", "1.52")
    gas_cols[1].metric("Winter $/Therm", "1.71")
    gas_cols[2].metric("Non-Winter $/Therm", "1.38")
    gas_cols[3].metric("Marginal GHG Tons/Therm", "0.0053")

    gas_chart_data = load_gas_chart_data()
    gas_chart = alt.Chart(gas_chart_data).mark_bar().encode(
        x="Month:O",
        y="$ / Therm:Q",
        color="Component:N"
    ).properties(title="Monthly Gas Costs by Component")
    st.altair_chart(gas_chart, use_container_width=True)

    st.line_chart(pd.DataFrame({
        "Year": list(range(2024, 2034)),
        "$ / Therm": [1.7 - i*0.02 for i in range(10)]
    }).set_index("Year"))

    gas_table = load_gas_table()
    st.dataframe(gas_table)
