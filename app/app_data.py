from dataclasses import dataclass

import duckdb
import streamlit as st
import pandas as pd


@st.cache_resource
def get_duckdb_connection():
    con = duckdb.connect("output/california.db")
    # df = pd.read_csv("data.csv")
    # con.register("avoided_costs", df)
    return con

def load_value_streams():
    return {
        "Cap and Trade": "#0072B2",
        "Capacity": "#56B4E9",
        "Energy": "#D55E00",
        "Losses": "#FCAEB7",
        "Transmission": "#009E73"
    }

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

@dataclass
class CalculationResults:
    net_lifecycle_mwh_savings: float
    net_lifecycle_therm_savings: float
    total_system_benefit: float
    # tsb_per_mwh: float
    ghg_savings_tons: float
    trc: float
    pac: float


def load_calculation_results():
    conn = get_duckdb_connection()
    res = conn.execute("""
        SELECT 
            round(electric_benefits, 0) as electric_benefits,
            round(gas_benefits, 0) as gas_benefits,
            round(lifecycle_total_ghg_savings, 0) as lifecycle_total_ghg_savings,
            round(total_benefits, 0) as total_benefits,
            round(trc_ratio, 0) as trc_ratio,
            round(pac_ratio, 0) as pac_ratio,
        FROM openbca.project_value_stream_benefits
        WHERE project_id = 'MAR100628'
    """)
    result = res.fetchone()
    print(res.description)
    print(result)
    row_dict = dict(zip([desc[0] for desc in res.description], result))
    return CalculationResults(
        # net_lifecycle_mwh_savings = 100.0,
        # net_lifecycle_therm_savings = 200.0,
        # total_system_benefit = 500000.0,
        # tsb_per_mwh = 5000.0,
        # ghg_savings_tons = 1000.0,
        # trc = 0.62,
        # pac = 1.20
        net_lifecycle_mwh_savings=row_dict['electric_benefits'], # result[0],
        net_lifecycle_therm_savings=result[1],
        total_system_benefit=result[2],
        ghg_savings_tons=result[3],
        trc=result[4],
        pac=result[5]
    )
