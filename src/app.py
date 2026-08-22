# src/app.py
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# 0. Path Resolution Fix
# Forces Python to look in the main project root instead of just the src/ folder
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.pipeline import run_pipeline
from src.normalize.adjust import COL_DATA

# 1. Page Configuration
st.set_page_config(
    page_title="Comp Equivalence Engine", 
    page_icon="🌍", 
    layout="wide"
)

st.title("🌍 Compensation Equivalence Engine")
st.markdown("Compare cross-border compensation using statutory tax modeling, PPP, and Cost of Living indices.")

# 2. Sidebar Inputs
st.sidebar.header("Calculation Parameters")
country_options = {
    "IN": "India (INR)", 
    "US": "United States (USD)", 
    "DE": "Germany (EUR)", 
    "JP": "Japan (JPY)"
}

selected_country_code = st.sidebar.selectbox(
    "Country", 
    options=list(country_options.keys()), 
    format_func=lambda x: country_options[x]
)

# Dynamically populate cities based on the selected country
available_cities = list(COL_DATA["cities"][selected_country_code].keys())
selected_city = st.sidebar.selectbox("City", options=available_cities)

# Default starting values based on currency
default_salary = {
    "IN": 2500000.0,
    "US": 100000.0,
    "DE": 80000.0,
    "JP": 9000000.0
}

gross_salary = st.sidebar.number_input(
    "Gross Annual Salary", 
    min_value=0.0, 
    value=default_salary[selected_country_code], 
    step=1000.0
)

# 3. Execution & Display
if st.sidebar.button("Calculate Equivalence", type="primary"):
    try:
        results = run_pipeline(gross_salary, selected_country_code, selected_city)
        
        inp = results["input"]
        tax = results["tax"]
        norm = results["normalized"]
        meta = results["metadata"]
        
        st.header(f"Results for {selected_city}, {selected_country_code}")
        
        # Tax Breakdown Row
        st.subheader("Statutory Tax Breakdown (2024 Base)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Gross Salary", f"{inp['gross_salary']:,.2f} {inp['currency']}")
        col2.metric("Net Local Pay", f"{tax['net_local']:,.2f} {inp['currency']}")
        col3.metric("Effective Tax Rate", f"{tax['effective_tax_rate_pct']:.2f}%")
        
        st.divider()
        
        # Normalization Row
        st.subheader("Normalized Equivalence Metrics")
        ncol1, ncol2, ncol3 = st.columns(3)
        ncol1.metric("Nominal USD (Market FX)", f"${norm['nominal_usd']:,.2f}")
        ncol2.metric("PPP Equivalence (Int$)", f"${norm['ppp_int_dollars']:,.2f}")
        ncol3.metric("COL-Adjusted (NYC Base)", f"${norm['col_adjusted_usd']:,.2f}")
        
        st.divider()
        
        # Dynamic Bar Chart
        st.subheader("Value Comparison (USD Equivalent)")
        chart_data = pd.DataFrame(
            {
                "Metric": ["Nominal USD", "PPP Int$", "COL-Adjusted (NYC)"],
                "Value": [norm["nominal_usd"], norm["ppp_int_dollars"], norm["col_adjusted_usd"]]
            }
        )
        st.bar_chart(chart_data.set_index("Metric"))
        
        # Metadata Footer
        st.caption(f"**Data Provenance** | FX Snapshot: {meta['fx_snapshot_date']} | World Bank PPP Base Year: {meta['ppp_indicator_year']}")
        
    except Exception as e:
        st.error(f"Error executing calculation: {e}")