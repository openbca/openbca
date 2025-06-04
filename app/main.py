import hashlib

import altair as alt

from app_data import *

st.set_page_config(layout="wide")

# hide header
st.markdown("""<style> .block-container {padding-top: 1rem;} header[data-testid="stHeader"] {height: 0px;visibility: hidden;} </style>""", unsafe_allow_html=True)

st.markdown("# OpenBCA")

COLORS = [
    "#0072B2",  # Blue
    "#56B4E9",  # Light Blue
    "#D55E00",  # Vermilion
    "#FCAEB7",  # Light Pink
    "#009E73",  # Bluish Green
    "#CC79A7",  # Reddish Purple
    "#E69F00",  # Orange
    "#999999",  # Grey
    "#F0E442",  # Yellow
    "#000000",  # Black
    "#003366",  # Dark Navy
    "#3399FF",  # Sky Blue
    "#990000",  # Dark Red
    "#FF6666",  # Salmon
    "#33CC99",  # Aquamarine
    "#660066",  # Deep Purple
    "#999933",  # Olive
    "#66CCCC",  # Teal
    "#FFCC00",  # Golden Yellow
    "#666699",  # Slate Blue
]

def get_color_for_value(value: str) -> str:
    """Assign a stable color to a given value using hashing."""
    idx = int(hashlib.sha256(value.encode()).hexdigest(), 16) % len(COLORS)
    return COLORS[idx]

def colorize_multiselect_stable(values: list[str]):
    """Inject CSS that colors tags based on their order, assuming stable option order."""
    css = ""
    for i, value in enumerate(values):
        color = get_color_for_value(value)
        # nth-child is 1-based, Streamlit renders in order
        css += f"""
        .stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({i+1}) {{
            background-color: {color} !important;
            color: white !important;
        }}
        """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def get_color(value: str, options: list[str]) -> str:
    """Assign a color based on value's position in options list."""
    index = options.index(value)
    return COLORS[index % len(COLORS)]

def inject_color_styles(selected_values: list[str], options: list[str], widget_key):
    """Inject CSS for multiselect tags based on option position (not tag position)."""
    css = ""
    for val in selected_values:
        index = selected_values.index(val)
        color = get_color(val, options)
        css += f"""
        .st-key-{widget_key} .stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({index + 1}) {{
            background-color: {color} !important;
            color: white !important;
        }}
        """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def impact_selection(commodity: str):
    #st.markdown(f"#### Impacts")
    value_streams_df = load_value_streams()
    value_streams_df = value_streams_df[value_streams_df['commodity'] == commodity]
    options = sorted(value_streams_df['cost_type'].unique().tolist())  # sorted = stable order

    widget_key = f"{commodity}_multiselect"
    selected = st.multiselect(
        f"Select value streams for {commodity}",
        options,
        default=options,
        key=widget_key,
    )

    #inject_color_styles(selected, options, widget_key)

    return selected

main_cols = st.columns([2, 3])

with main_cols[0]:

    with st.expander("Inputs", expanded=True):
        filter_rows = st.columns(4)

        with filter_rows[0]:
            #st.markdown("#### Utility & Location")
            utility = st.selectbox("Utility", ["PGE"])
            region = st.selectbox("Region", ['CZ12', 'CZ2', 'CZ3A', 'CZ3B', 'CZ12'])

        with filter_rows[1]:
            #st.markdown("#### Time Period")
            start_year = st.number_input("Start Year", value=2021, step=1)
            start_quarter = st.selectbox("Start Quarter", [1, 2, 3, 4])

        with filter_rows[2]:
            #st.markdown("#### Financial Inputs")
            eul = st.number_input("EUL", value=10)
            discount_rate = st.number_input("Discount Rate", value=0.075)

        with filter_rows[3]:
            #st.markdown("#### Additional Inputs")
            units = st.number_input("Units", value=1, step=1)
            ntg = st.number_input("NTG", value=1.0, step=0.01)

        costs_col = st.columns(3)
        #st.markdown("#### Cost Information")
        with costs_col[0]:
            admin_cost = st.number_input("Administrative Cost", value=3000)
        with costs_col[1]:
            incentive_cost = st.number_input("Incentive Cost", value=500)
        with costs_col[2]:
            measure_cost = st.number_input("Measure Cost", value=1000)

        commodity_input_tabs = st.tabs(["Electricity", "Gas"])

        with commodity_input_tabs[0]:
            elec_commodity_cols = st.columns(2)
            # st.markdown("#### Electric Saving and Load Shape")
            with elec_commodity_cols[0]:
                electric_curve = st.selectbox("Electric Value Curve", ["NONRES_INDOOR_CFL_LTG", "NONRES_HVAC_SPLIT_PACKAGE_AC"])
            with elec_commodity_cols[1]:
                mwh_savings = st.number_input("Annual MWh saving", value=10)

            electricity_impact_selection = impact_selection('ELECTRICITY') #TODO

        with commodity_input_tabs[1]:
            gas_commodity_cols = st.columns(2)
            with gas_commodity_cols[0]:
                gas_curve = st.selectbox("Gas Value Curve", ["annual"])
            with gas_commodity_cols[1]:
                therms_savings = st.number_input("Annual Therms saving", value=100)

            gas_impact_selection = impact_selection('GAS')

        refresh_project_table(
            utility=utility, region=region,
            start_year=start_year, start_quarter=start_quarter,
            discount_rate=discount_rate, eul=eul,
            units=units, ntg=ntg,
            mwh_savings=mwh_savings, load_shape=electric_curve,
            therms_savings=therms_savings, therms_profile=gas_curve,
            admin_cost=admin_cost, incentive_cost=incentive_cost, measure_cost=measure_cost,
        )

with main_cols[1]:

    #st.markdown("## Total System Benefits")

    def f_n(value: float) -> str:
        return f"{value:,.0f}"

    def f_n_2(value: float) -> str:
        return f"{value:,.2f}"

    def render_metric(name: str, value: float, details: str = ""):
        st.markdown(f"""
            <div style='padding: 10px; border: 1px solid #ccc; border-radius: 10px;'>
                <strong>{name}</strong><br>
                <span style='font-size: 24px;'>{f_n_2(value) if name in {'TRC', 'PAC'} else f_n(value)}</span><br>
                {details}
            </div>
        """, unsafe_allow_html=True)


    result = load_impacts_df(electricity_impact_selection, gas_impact_selection)

    with st.container():
        row_top = st.columns(2)
        with row_top[0]:
            render_metric("Net Lifecycle MWh Savings", result[PROJECT_IMPACT_ELECTRIC_BENEFITS])
        with row_top[1]:
            render_metric("Net Lifecycle Therm Savings", result[PROJECT_IMPACT_GAS_BENEFITS])

        st.markdown(" ")
        row_mid = st.columns([2, 1.5, 2, 1, 1])

        with row_mid[0]:
            render_metric(
                "Total System Benefit", result[PROJECT_IMPACT_TOTAL_BENEFITS],
                f"<small>Electric: {f_n(result[PROJECT_IMPACT_ELECTRIC_BENEFITS])} | Gas: {f_n(result[PROJECT_IMPACT_GAS_BENEFITS])}</small>"
            )
        with row_mid[1]:
            render_metric("TSB/MWh", result[PROJECT_IMPACT_TOTAL_BENEFITS_PER_MWH], f"<small>TSB/Therm: {result[PROJECT_IMPACT_TOTAL_BENEFITS_PER_THERM]}</small>")
        with row_mid[2]:
            render_metric(
                "GHG Savings (Tons)", result[PROJECT_IMPACT_TOTAL_GHG_BENEFITS],
                f"<small>Electric: {f_n(result[PROJECT_IMPACT_ELECTRIC_GHG_BENEFITS])} | Gas: {f_n(result[PROJECT_IMPACT_GAS_GHG_BENEFITS])}</small>"
            )
        with row_mid[3]:
            render_metric("TRC", result[PROJECT_IMPACT_TRC_RATIO])
        with row_mid[4]:
            render_metric("PAC", result[PROJECT_IMPACT_PAC_RATIO])

    energy_tabs = st.tabs(["Electricity", "Gas"])

    with energy_tabs[0]:
        # st.markdown("## Electricity")
        # electric_cols = st.columns(4)
        # electric_cols[0].metric("$/MWh", "67.50")
        # electric_cols[1].metric("Peak $/MWh", "368.89")
        # electric_cols[2].metric("Off Peak $/MWh", "44.94")
        # electric_cols[3].metric("Marginal GHG Tons/MWh", "0.32")

        electric_chart_data = load_electric_chart_data(electricity_impact_selection)
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
        #st.altair_chart(line_chart, use_container_width=True)

        #electric_table = load_electric_table()
        #st.dataframe(electric_table)


    with energy_tabs[1]:
        # st.markdown("## Gas")
        # gas_cols = st.columns(4)
        # gas_cols[0].metric("$/Therm", "1.52")
        # gas_cols[1].metric("Winter $/Therm", "1.71")
        # gas_cols[2].metric("Non-Winter $/Therm", "1.38")
        # gas_cols[3].metric("Marginal GHG Tons/Therm", "0.0053")

        gas_chart_data = load_gas_chart_data(gas_impact_selection)
        gas_chart = alt.Chart(gas_chart_data).mark_bar().encode(
            x="Month:O",
            y="$ / Therm:Q",
            color="Component:N"
        ).properties(title="Monthly Gas Costs by Component")
        st.altair_chart(gas_chart, use_container_width=True)

        # st.line_chart(pd.DataFrame({
        #     "Year": list(range(2024, 2034)),
        #     "$ / Therm": [1.7 - i*0.02 for i in range(10)]
        # }).set_index("Year"))

        gas_line_chart = alt.Chart(peak_offpeak_df).mark_line(point=True).encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("$ / MWh:Q", title="$ / MWh"),
            color=alt.Color("Type:N", scale=alt.Scale(domain=["peak", "off_peak"], range=["blue", "red"])),
            strokeDash="Type"
        ).properties(title="Peak Period = June - Sept, 4 - 9 pm     *Discount Rate Applied")
        #st.altair_chart(gas_line_chart, use_container_width=True)

        #gas_table = load_gas_table()
        #st.dataframe(gas_table)
