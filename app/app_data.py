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
        ORDER BY commodity, cost_type
    """).fetch_df()

    return df

def load_electric_chart_data(elec_costs):
    return get_connection().execute(f"""
        SELECT hour_of_day as "Hour of Day", cost_type AS Category, round(SUM(av_cost_value), 0) AS "$ / MWh"
        FROM app.openbca.project_commodity_impact_ts
        WHERE project_id = '{PROJECT_ID}'
        AND commodity = 'ELECTRICITY'
        AND cost_type IN ({','.join([f"'{c}'" for c in elec_costs])})
        GROUP BY hour_of_day, cost_type
    """).fetch_df()

def load_gas_chart_data(gas_costs):
    return get_connection().execute(f"""
        SELECT month as Month, cost_type AS Component, round(SUM(av_cost_value), 2) AS "$ / Therm"
        FROM app.openbca.project_commodity_impact_ts
        WHERE project_id = '{PROJECT_ID}'
        AND commodity = 'GAS'
        AND cost_type IN ({','.join([f"'{c}'" for c in gas_costs])})
        GROUP BY month, cost_type
    """).fetch_df()


def load_impacts_df(elec_costs, gas_costs):
    query = f"""
        SELECT *,
            {PROJECT_IMPACT_ELECTRIC_BENEFITS} + {PROJECT_IMPACT_GAS_BENEFITS}
                AS {PROJECT_IMPACT_TOTAL_BENEFITS},
            {PROJECT_IMPACT_ELECTRIC_GHG_BENEFITS} + {PROJECT_IMPACT_GAS_GHG_BENEFITS}
                AS {PROJECT_IMPACT_TOTAL_GHG_BENEFITS},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS}::float + {PROJECT_IMPACT_GAS_BENEFITS}::float) / trc_costs
                AS {PROJECT_IMPACT_TRC_RATIO},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS}::float + {PROJECT_IMPACT_GAS_BENEFITS}::float) / pac_costs
                AS {PROJECT_IMPACT_PAC_RATIO},
            {PROJECT_IMPACT_ELECTRIC_BENEFITS}::float / {PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS} 
                AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_MWH},                           
            {PROJECT_IMPACT_GAS_BENEFITS}::float / {PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS}::float 
                AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_THERM}
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
        FROM openbca.project_commodity_impacts
        WHERE project_id = '{PROJECT_ID}'
        AND (
            ( commodity = 'ELECTRICITY' AND cost_type IN ({','.join([f"'{c}'" for c in elec_costs])}) )
            OR ( commodity = 'GAS' AND cost_type IN ({','.join([f"'{c}'" for c in gas_costs])}) )
        )
        ) JOIN project.project_costs ON project_id = '{PROJECT_ID}'
    """
    print(query)
    res = get_connection().execute(query, ).fetch_df()

    return res.iloc[0].to_dict()

@st.cache_resource
def get_context():
    return Context(config=load_configs(None, Context.CONFIG_TYPE, "profiles/app"))

def refresh_project_table(**kwargs):
    """
    Refreshes the project table with the provided parameters like eul=2, utility='PG&E', region='CA', etc.
    """
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
    context.apply(context.plan('app'))
