from sqlmesh import Context
from sqlmesh.core.config import load_configs
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st
import pandas as pd
import duckdb

PROJECT_ID = get_script_run_ctx().session_id

INPUT_PROJECT_FIELDS = ['utility', 'region', 'start_year', 'start_quarter', 'discount_rate', 'eul', 'units', 'ntg', 'admin_cost', 'incentive_cost', 'measure_cost', 'mwh_savings', 'therms_savings', 'load_shape', 'therms_profile']

PROJECT_IMPACT_ELECTRIC_BENEFITS = "electric_benefits"
PROJECT_IMPACT_TOTAL_BENEFITS = "total_benefits"
PROJECT_IMPACT_GAS_BENEFITS = "gas_benefits"

PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS = "net_electric_energy_savings"
PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS = "net_gas_energy_savings"

PROJECT_IMPACT_TOTAL_BENEFITS_PER_MWH = "total_benefits_per_mwh"
PROJECT_IMPACT_TOTAL_BENEFITS_PER_THERM = "total_benefits_per_therm"

PROJECT_IMPACT_ELECTRIC_GHG_BENEFITS = "electric_ghg_benefits"
PROJECT_IMPACT_GAS_GHG_BENEFITS = "gas_ghg_benefits"
PROJECT_IMPACT_TOTAL_GHG_BENEFITS = "total_ghg_benefits"

PROJECT_IMPACT_TRC_RATIO = "trc_ratio"
PROJECT_IMPACT_PAC_RATIO = "pac_ratio"

@st.cache_resource
def get_connection():
    return duckdb.connect("output/app.db", read_only=False)

def load_value_streams():
    df = get_connection().execute(f"""
        SELECT DISTINCT commodity, cost_type
        FROM app.openbca_input.avoided_costs_ts
        WHERE cost_type NOT IN ('total')
        --AND cost_type IN ('btm_methane', 'cap_and_trade', 'capacity', 't_d')
        ORDER BY commodity, cost_type
    """).fetch_df()

    return df

def load_electric_chart_data():
    return pd.DataFrame({
        "Hour of Day": list(range(24)) * 5,
        "$ / MWh": [20] * 24 + [5] * 24 + [3] * 24 + [10 if i in [17, 18, 19] else 2 for i in range(24)] + [1] * 24,
        "Category": ["Energy"] * 24 + ["Losses"] * 24 + ["Cap and Trade"] * 24 + ["Capacity"] * 24 + [
            "Transmission"] * 24
    })

def load_electric_table():
    return pd.DataFrame({
        "Year": [2025] * 10,
        "Month": [2] * 10,
        "Hour of Day": list(range(10, 20)),
        "$ / MWh": [round(30 + i * 2 + (i % 3) * 10, 2) for i in range(10)]
    })


def load_peak_offpeak():
    years = list(range(2024, 2034))
    peak = [625, 550, 500, 475, 450, 425, 400, 225, 230, 200]
    off_peak = [55, 52, 50, 48, 47, 46, 45, 44, 43, 42]
    return pd.DataFrame({
        "Year": years * 2,
        "$ / MWh": peak + off_peak,
        "Type": ["peak"] * 10 + ["off_peak"] * 10
    })


def load_gas_chart_data():
    return pd.DataFrame({
        "Month": list(range(1, 13)),
        "$ / Therm": [1.6 if m in [1, 2, 3, 11, 12] else 1.4 for m in range(1, 13)],
        "Component": ["Market"] * 12
    })


def load_gas_table():
    return pd.DataFrame({
        "Year": [2024] * 12,
        "Month": list(range(1, 13)),
        "$ / Therm": [round(2 - i * 0.05, 2) for i in range(12)]
    })

def load_impacts_df(elec_costs, gas_costs):
    query = f"""
        SELECT *,
            {PROJECT_IMPACT_ELECTRIC_BENEFITS} + {PROJECT_IMPACT_GAS_BENEFITS}
                AS {PROJECT_IMPACT_TOTAL_BENEFITS},
            {PROJECT_IMPACT_ELECTRIC_GHG_BENEFITS} + {PROJECT_IMPACT_GAS_GHG_BENEFITS}
                AS {PROJECT_IMPACT_TOTAL_GHG_BENEFITS},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS} + {PROJECT_IMPACT_GAS_BENEFITS}) / trc_costs
                as {PROJECT_IMPACT_TRC_RATIO},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS} + {PROJECT_IMPACT_GAS_BENEFITS}) / pac_costs
                as {PROJECT_IMPACT_PAC_RATIO},
            {PROJECT_IMPACT_ELECTRIC_BENEFITS} / {PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS} AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_MWH},                           
            {PROJECT_IMPACT_GAS_BENEFITS} / {PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS} AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_THERM}
        FROM ( SELECT
            SUM(CASE WHEN cost_type <> 'marginal_ghg' AND commodity = 'ELECTRICITY' THEN impact_value ELSE 0 END)
                AS {PROJECT_IMPACT_ELECTRIC_BENEFITS},
            SUM(CASE WHEN cost_type <> 'marginal_ghg' AND commodity = 'GAS' THEN impact_value ELSE 0 END)
                AS {PROJECT_IMPACT_GAS_BENEFITS},
            SUM(CASE WHEN cost_type = 'marginal_ghg' AND commodity = 'ELECTRICITY' THEN impact_value ELSE 0 END)
                AS {PROJECT_IMPACT_ELECTRIC_GHG_BENEFITS},
            SUM(CASE WHEN cost_type = 'marginal_ghg' AND commodity = 'GAS' THEN impact_value ELSE 0 END)
                AS {PROJECT_IMPACT_GAS_GHG_BENEFITS},
            SUM(CASE WHEN commodity = 'ELECTRICITY' THEN net_energy_savings ELSE 0 END)
                AS {PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS},
            SUM(CASE WHEN commodity = 'GAS' THEN net_energy_savings ELSE 0 END)
                AS {PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS},                
        FROM app.openbca.project_commodity_impacts
        WHERE project_id = '{PROJECT_ID}'
        AND (
            ( commodity = 'ELECTRICITY' AND cost_type IN ({','.join([f"'{c}'" for c in elec_costs])}) )
            OR ( commodity = 'GAS' AND cost_type IN ({','.join([f"'{c}'" for c in gas_costs])}) )
        )
        ) JOIN project.project_costs ON project_id = '{PROJECT_ID}'
    """
    print(query)
    res = get_connection().execute(query, ).fetch_df()

    float_columns = res.select_dtypes(include=['float64']).columns
    for col in float_columns:
        res[col] = res[col].round(0).astype(pd.Int64Dtype(), errors='ignore')

    return res.iloc[0].to_dict()

@st.cache_resource
def get_context():
    return Context(config=load_configs(None, Context.CONFIG_TYPE, "profiles/app"))

def refresh_project_table(**kwargs):
    project_fields = [field for field in INPUT_PROJECT_FIELDS if field in kwargs]
    project_values = [kwargs[field] for field in project_fields]

    get_connection().execute(f"""
        INSERT INTO app.app_tmp.empty_projects (project_id, {', '.join(project_fields)}) 
        VALUES ('{PROJECT_ID}', {','.join('?' * len(project_fields))})
        ON CONFLICT DO UPDATE SET {', '.join([f"{field} = EXCLUDED.{field}" for field in project_fields])};
    """, project_values)

    recalculate_impacts()


def recalculate_impacts():
    context = get_context()
    context.apply(context.plan("openbca.project_impacts"))
