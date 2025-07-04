import os

import streamlit as st
import duckdb

INPUT_PROJECT_FIELDS = ['avoided_cost_subset', 'start_year', 'start_quarter', 'discount_rate', 'eul', 'units', 'ntg', 'admin_cost', 'incentive_cost', 'measure_cost', 'mwh_savings', 'therms_savings', 'load_shape', 'therms_profile']

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
    return duckdb.connect(os.environ['DB'], read_only=False)

def get_value_streams():
    return get_connection().execute(f"""
        SELECT DISTINCT commodity, avoided_cost
        FROM openbca_reference.avoided_costs_ts
        ORDER BY commodity, avoided_cost
    """).fetch_df()

def get_electricity_impacts_by_avoided_cost_ts(project_id: str, elec_costs: list[str]):
    return get_connection().execute(f"""
        SELECT hour_of_day as "Hour of Day", avoided_cost AS Category, round(SUM(av_cost_value), 0) AS "$ / MWh"
        FROM openbca_impact.project_commodity_impact_ts
        WHERE project_id = '{project_id}'
        AND commodity = 'ELECTRICITY'
        AND avoided_cost IN ({','.join([f"'{c}'" for c in elec_costs])})
        GROUP BY hour_of_day, avoided_cost
    """).fetch_df()

def get_gas_impacts_by_avoided_cost_ts(project_id: str, gas_costs: list[str]):
    return get_connection().execute(f"""
        SELECT month as Month, avoided_cost AS Component, round(SUM(av_cost_value), 2) AS "$ / Therm"
        FROM openbca_impact.project_commodity_impact_ts
        WHERE project_id = '{project_id}'
        AND commodity = 'GAS'
        AND avoided_cost IN ({','.join([f"'{c}'" for c in gas_costs])})
        GROUP BY month, avoided_cost
    """).fetch_df()

def get_project_impacts(project_id: str, elec_costs: list[str], gas_costs: list[str]):
    query = f"""
        SELECT *,
            {PROJECT_IMPACT_ELECTRIC_BENEFITS} + {PROJECT_IMPACT_GAS_BENEFITS}
                AS {PROJECT_IMPACT_TOTAL_BENEFITS},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS}::float + {PROJECT_IMPACT_GAS_BENEFITS}::float) / trc_costs
                AS {PROJECT_IMPACT_TRC_RATIO},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS}::float + {PROJECT_IMPACT_GAS_BENEFITS}::float) / pac_costs
                AS {PROJECT_IMPACT_PAC_RATIO},
            {PROJECT_IMPACT_ELECTRIC_BENEFITS}::float / {PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS} 
                AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_MWH},                           
            {PROJECT_IMPACT_GAS_BENEFITS}::float / {PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS}::float 
                AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_THERM}            
        FROM openbca_impact.project_impacts
        WHERE project_id = '{project_id}'
        AND (
            ( commodity = 'ELECTRICITY' AND avoided_cost IN ({','.join([f"'{c}'" for c in elec_costs])}) )
            OR ( commodity = 'GAS' AND avoided_cost IN ({','.join([f"'{c}'" for c in gas_costs])}) )
        )
        ) JOIN project.project_costs ON project_id = '{project_id}'
    """
    print(query)
    res = get_connection().execute(query, ).fetch_df()

    return res.iloc[0].to_dict()

def get_project_impacts_old(project_id: str, elec_costs: list[str], gas_costs: list[str]):
    query = f"""
        SELECT *,
            {PROJECT_IMPACT_ELECTRIC_BENEFITS} + {PROJECT_IMPACT_GAS_BENEFITS}
                AS {PROJECT_IMPACT_TOTAL_BENEFITS},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS}::float + {PROJECT_IMPACT_GAS_BENEFITS}::float) / trc_costs
                AS {PROJECT_IMPACT_TRC_RATIO},
            ({PROJECT_IMPACT_ELECTRIC_BENEFITS}::float + {PROJECT_IMPACT_GAS_BENEFITS}::float) / pac_costs
                AS {PROJECT_IMPACT_PAC_RATIO},
            {PROJECT_IMPACT_ELECTRIC_BENEFITS}::float / {PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS} 
                AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_MWH},                           
            {PROJECT_IMPACT_GAS_BENEFITS}::float / {PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS}::float 
                AS {PROJECT_IMPACT_TOTAL_BENEFITS_PER_THERM}
        FROM ( SELECT
            SUM(CASE WHEN commodity = 'ELECTRICITY' THEN impact_dollars ELSE 0 END)
                AS {PROJECT_IMPACT_ELECTRIC_BENEFITS},
            SUM(CASE WHEN commodity = 'GAS' THEN impact_dollars ELSE 0 END)
                AS {PROJECT_IMPACT_GAS_BENEFITS},        
            SUM(CASE WHEN commodity = 'ELECTRICITY' THEN net_energy_savings ELSE 0 END)
                AS {PROJECT_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS},
            SUM(CASE WHEN commodity = 'GAS' THEN net_energy_savings ELSE 0 END)
                AS {PROJECT_IMPACT_NET_GAS_ENERGY_SAVINGS},                
        FROM openbca_impact.project_commodity_economic_impacts
        WHERE project_id = '{project_id}'
        AND (
            ( commodity = 'ELECTRICITY' AND avoided_cost IN ({','.join([f"'{c}'" for c in elec_costs])}) )
            OR ( commodity = 'GAS' AND avoided_cost IN ({','.join([f"'{c}'" for c in gas_costs])}) )
        )
        ) JOIN project.project_costs ON project_id = '{project_id}'
    """
    print(query)
    res = get_connection().execute(query, ).fetch_df()

    return res.iloc[0].to_dict()

# @st.cache_resource
# def get_context():
#     return Context(config=load_configs(None, Context.CONFIG_TYPE, "profiles/app"))

def update_project(project_id: str, **kwargs):
    """
    Refreshes the project table with the provided parameters like eul=2, utility='PG&E', region='CA', etc.
    """
    project_fields = [field for field in INPUT_PROJECT_FIELDS if field in kwargs]
    project_values = [kwargs[field] for field in project_fields]

    get_connection().execute(f"""
        INSERT INTO openbca_user_input.user_projects (project_id, {', '.join(project_fields)}) 
        VALUES ('{project_id}', {','.join('?' * len(project_fields))})
        ON CONFLICT DO UPDATE SET {', '.join([f"{field} = EXCLUDED.{field}" for field in project_fields])};
    """, project_values)

    #recalculate_impacts()


# def recalculate_impacts():
#     context = get_context()
#     context.apply(context.plan('app'))

def get_avoided_cost_subsets()->list[str]:
    return get_connection().execute(f"""
        SELECT DISTINCT avoided_cost_subset
        FROM openbca_reference.avoided_costs_ts
        ORDER BY avoided_cost_subset
    """).fetch_df().avoided_cost_subset.tolist()

def get_electricity_value_curves():
    return get_connection().execute(f"""
        SELECT distinct load_shape 
        FROM openbca_reference.commodity_load_shape_ts 
        where commodity = 'ELECTRICITY'
        ORDER BY load_shape
    """).fetch_df().load_shape.tolist()


def get_gas_value_curves():
    return get_connection().execute(f"""
        SELECT distinct load_shape 
        FROM openbca_reference.commodity_load_shape_ts 
        where commodity = 'GAS'
        ORDER BY load_shape
    """).fetch_df().load_shape.tolist()
