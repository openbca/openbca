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
    tsb_per_mwh: float
    ghg_savings_tons: float
    trc: float
    pac: float


def load_calculation_results():
    return CalculationResults(
        net_lifecycle_mwh_savings = 100.0,
        net_lifecycle_therm_savings = 200.0,
        total_system_benefit = 500000.0,
        tsb_per_mwh = 5000.0,
        ghg_savings_tons = 1000.0,
        trc = 0.62,
        pac = 1.20
    )
