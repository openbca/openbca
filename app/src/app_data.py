import os

import streamlit as st
import duckdb

INPUT_MEASURE_FIELDS = ['avoided_cost_subset', 'start_year', 'start_quarter', 'discount_rate_ratio', 'estimated_useful_life', 'unit_quantity', 'net_to_gross_ratio', 'admin_cost_dollars', 'incentive_cost_dollars', 'measure_cost_dollars', 'elec_savings_mwh', 'gas_saving_therms', 'elec_load_shape_mapping', 'gas_load_shape_mapping']

MEASURE_IMPACT_ELECTRIC_BENEFITS = "electric_benefits"
MEASURE_IMPACT_TOTAL_BENEFITS = "total_benefits"
MEASURE_IMPACT_GAS_BENEFITS = "gas_benefits"

MEASURE_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS = "net_electric_energy_savings"
MEASURE_IMPACT_NET_GAS_ENERGY_SAVINGS = "net_gas_energy_savings"

MEASURE_IMPACT_TOTAL_BENEFITS_PER_MWH = "total_benefits_per_mwh"
MEASURE_IMPACT_TOTAL_BENEFITS_PER_THERM = "total_benefits_per_therm"

MEASURE_IMPACT_ELECTRIC_GHG_BENEFITS = "electric_ghg_savings"
MEASURE_IMPACT_GAS_GHG_BENEFITS = "gas_ghg_savings"
MEASURE_IMPACT_TOTAL_GHG_BENEFITS = "total_ghg_benefits"

MEASURE_IMPACT_TRC_RATIO = "trc_ratio"
MEASURE_IMPACT_PAC_RATIO = "pac_ratio"

@st.cache_resource
def get_connection():
    return duckdb.connect(os.environ.get('DB', 'output/openbca.db'), read_only=False)

def get_value_streams():
    return get_connection().execute(f"""
        SELECT DISTINCT commodity, avoided_cost
        FROM openbca_reference.avoided_costs_ts
        ORDER BY commodity, avoided_cost
    """).fetch_df()

def get_electricity_impacts_by_avoided_cost_ts(measure_id: str, elec_costs: list[str]):
    return get_connection().execute(f"""
        SELECT hour_of_day as "Hour of Day", avoided_cost AS Category, round(SUM(av_cost_dollar_per_energy_unit), 0) AS "$ / MWh"
        FROM openbca_core.measure_commodity_impact_ts
        WHERE measure_id = '{measure_id}'
        AND commodity = 'ELECTRICITY'
        AND avoided_cost IN ({','.join([f"'{c}'" for c in elec_costs])})
        GROUP BY hour_of_day, avoided_cost
    """).fetch_df()

def get_gas_impacts_by_avoided_cost_ts(measure_id: str, gas_costs: list[str]):
    return get_connection().execute(f"""
        SELECT month as Month, avoided_cost AS Component, round(SUM(av_cost_dollar_per_energy_unit), 2) AS "$ / Therm"
        FROM openbca_core.measure_commodity_impact_ts
        WHERE measure_id = '{measure_id}'
        AND commodity = 'GAS'
        AND avoided_cost IN ({','.join([f"'{c}'" for c in gas_costs])})
        GROUP BY month, avoided_cost
    """).fetch_df()

def get_measure_impacts(measure_id: str):
    conn = get_connection()

    # Totals and ratios from core
    totals = conn.execute(f"""
        SELECT total_benefits, trc_ratio, pac_ratio, total_ghg_benefits
        FROM openbca_core.measure_impacts
        WHERE measure_id = '{measure_id}'
    """).fetch_df()
    if totals.empty:
        # default zeros if no record
        totals_row = {
            'total_benefits': 0.0,
            'trc_ratio': 0.0,
            'pac_ratio': 0.0,
            'total_ghg_benefits': 0.0,
        }
    else:
        totals_row = totals.iloc[0].to_dict()

    # Economic breakdown by commodity
    econ = conn.execute(f"""
        SELECT commodity, SUM(impact_dollars) AS benefits, SUM(net_energy_savings) AS net_savings
        FROM openbca_core.measure_commodity_economic_impacts
        WHERE measure_id = '{measure_id}'
        GROUP BY commodity
    """).fetch_df()
    econ_dict = {row['commodity']: {'benefits': row['benefits'], 'net_savings': row['net_savings']} for _, row in econ.iterrows()}

    # Environmental breakdown by commodity
    env = conn.execute(f"""
        SELECT commodity, SUM(impact_tons_co2e) AS ghg
        FROM openbca_core.measure_commodity_environmental_impacts
        WHERE measure_id = '{measure_id}'
        GROUP BY commodity
    """).fetch_df()
    env_dict = {row['commodity']: row['ghg'] for _, row in env.iterrows()}

    # Pull values with safe defaults
    elec_benefits = float(econ_dict.get('ELECTRICITY', {}).get('benefits', 0.0))
    gas_benefits = float(econ_dict.get('GAS', {}).get('benefits', 0.0))
    elec_net = float(econ_dict.get('ELECTRICITY', {}).get('net_savings', 0.0))
    gas_net = float(econ_dict.get('GAS', {}).get('net_savings', 0.0))

    elec_ghg = float(env_dict.get('ELECTRICITY', 0.0))
    gas_ghg = float(env_dict.get('GAS', 0.0))

    def safe_div(a: float, b: float) -> float:
        return (a / b) if b not in (0, 0.0, None) else 0.0

    # Assemble the expected response dict for the app UI without changing the UI
    result = {
        MEASURE_IMPACT_ELECTRIC_BENEFITS: elec_benefits,
        MEASURE_IMPACT_GAS_BENEFITS: gas_benefits,
        MEASURE_IMPACT_TOTAL_BENEFITS: float(totals_row['total_benefits']),
        MEASURE_IMPACT_TRC_RATIO: float(totals_row['trc_ratio']),
        MEASURE_IMPACT_PAC_RATIO: float(totals_row['pac_ratio']),
        MEASURE_IMPACT_NET_ELECTRIC_ENERGY_SAVINGS: elec_net,
        MEASURE_IMPACT_NET_GAS_ENERGY_SAVINGS: gas_net,
        MEASURE_IMPACT_TOTAL_BENEFITS_PER_MWH: safe_div(elec_benefits, elec_net),
        MEASURE_IMPACT_TOTAL_BENEFITS_PER_THERM: safe_div(gas_benefits, gas_net),
        MEASURE_IMPACT_TOTAL_GHG_BENEFITS: float(totals_row['total_ghg_benefits']),
        MEASURE_IMPACT_ELECTRIC_GHG_BENEFITS: elec_ghg,
        MEASURE_IMPACT_GAS_GHG_BENEFITS: gas_ghg,
    }

    return result

def update_measure(measure_id: str, **kwargs):
    """
    Refreshes the measure table with the provided parameters like estimated_useful_life=2, utility='PG&E', region='CA', etc.
    """
    measure_fields = [field for field in INPUT_MEASURE_FIELDS if field in kwargs]
    measure_values = [kwargs[field] for field in measure_fields]

    get_connection().execute(f"""
        INSERT INTO openbca_app.measures (measure_id, {', '.join(measure_fields)}) 
        VALUES ('{measure_id}', {','.join('?' * len(measure_fields))})
        ON CONFLICT DO UPDATE SET {', '.join([f"{field} = EXCLUDED.{field}" for field in measure_fields])};
    """, measure_values)

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
