# src/app.py
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# 0. Path Resolution Fix
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

currency_labels = {
    "IN": "INR (₹)",
    "US": "USD ($)",
    "DE": "EUR (€)",
    "JP": "JPY (¥)"
}

default_salary = {
    "IN": 2500000,
    "US": 100000,
    "DE": 80000,
    "JP": 9000000
}

selected_country_code = st.sidebar.selectbox(
    "Country", 
    options=list(country_options.keys()), 
    format_func=lambda x: country_options[x]
)

# Dynamically populate cities based on selected country
available_cities = list(COL_DATA["cities"][selected_country_code].keys())
selected_city = st.sidebar.selectbox("City", options=available_cities)

# Job Role Selection
selected_role = st.sidebar.selectbox(
    "Job Role", 
    options=["Software Engineer", "Data Scientist", "Data Analyst"]
)

# Dynamic Gross Salary with matching currency label and clean integer formatting
curr_label = currency_labels[selected_country_code]
gross_salary = st.sidebar.number_input(
    f"Gross Annual Salary ({curr_label})", 
    min_value=0, 
    value=int(default_salary[selected_country_code]), 
    step=5000,
    format="%d"
)

# Formatted currency preview with commas
st.sidebar.caption(f"Formatted: **{gross_salary:,.0f} {curr_label}**")

# 3. Execution & Display
if st.sidebar.button("Calculate Equivalence", type="primary"):
    try:
        results = run_pipeline(float(gross_salary), selected_country_code, selected_city, selected_role)
        
        inp = results["input"]
        tax = results["tax"]
        norm = results["normalized"]
        bench = results["benchmark"]
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
        
        # Market Benchmark & Score Row
        st.subheader("Market Benchmark & Score")
        scol1, scol2 = st.columns(2)
        scol1.metric(f"Local Market Percentile ({bench['role']})", f"{bench['percentile']}th")
        scol2.metric("Overall Equivalence Score", f"{bench['overall_score_out_of_100']} / 100")
        
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
        
        # Day 7: Data Staleness Guard
        from datetime import datetime
        fx_date = datetime.strptime(meta['fx_snapshot_date'], "%Y-%m-%d")
        days_old = (datetime.now() - fx_date).days
        
        if days_old > 30:
            st.warning(f"⚠️ **Data Staleness Warning:** The Foreign Exchange (FX) data used for this calculation is {days_old} days old. Real-world equivalent values may have fluctuated.")
        
    except Exception as e:
        st.error(f"Error executing calculation: {e}")