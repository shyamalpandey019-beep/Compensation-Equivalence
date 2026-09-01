# EquivPay — Global Compensation Normalization Engine 🌍

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.1.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-21%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A high-fidelity cross-border compensation normalization engine that translates technical salaries across jurisdictions using 2024 progressive statutory tax brackets, World Bank purchasing power parity (PPP), localized cost-of-living indices (NYC Base 100), and verified tech role market percentiles.

**Live Dashboard**: [https://comp-engine.streamlit.app](https://comp-engine.streamlit.app)  
**Live API Docs**: [https://compensation-equivalence.onrender.com/docs](https://compensation-equivalence.onrender.com/docs)

![EquivPay Analysis Dashboard](dashboard.png)

---

## 💡 The Problem

Directly comparing international compensation offers using spot foreign exchange (FX) rates is fundamentally flawed. A **$140,000** salary in San Francisco does not provide the same standard of living as **€85,000** in Berlin, **¥11,000,000** in Tokyo, or **₹3,500,000** in Bangalore due to differing statutory tax schedules, mandatory social security contributions, and local purchasing power variations.

**EquivPay** solves this through a four-stage normalization pipeline that calculates statutory net take-home pay, adjusts for purchasing power parity (PPP) and metro cost of living (COL), and benchmarks the result against local tech percentiles.

---

## ✨ Core Features

- **Statutory Progressive Taxation**: Comprehensive 2024 tax modeling (Standard Deductions, Progressive Brackets, Surcharges, FICA Social Security/Medicare, Reconstruction Tax) for **India (IN)**, the **United States (US)**, **Germany (DE)**, and **Japan (JP)**.
- **Tri-Vector Normalization**:
  - **Nominal USD**: Spot conversion using European Central Bank reference exchange rates.
  - **PPP Int$**: World Bank International Dollar Purchasing Power Parity factor.
  - **COL-Adjusted USD**: Numbeo Cost of Living index anchored to New York City (NYC Base 100.0).
- **Cross-Border Parity Matrix**: Exact gross compensation required across major global hubs (San Francisco, Bangalore, Berlin, Tokyo) to maintain identical lifestyle purchasing power.
- **Market Percentile Benchmarking**: Continuous piecewise percentile interpolation (P25, Median, P75) across Software Engineers, Data Scientists, and Data Analysts.
- **Multi-Interface Access**: Interactive Web App (Streamlit + Tailwind Design System), Fast REST API (FastAPI), and scriptable CLI tool.

---

## ⚙️ Architecture & Pipeline Flow

```
[ Gross Salary + Jurisdiction + Metro + Role ]
                      │
                      ▼
 ┌──────────────────────────────────────────┐
 │ Stage 1: Statutory Progressive Waterfall │  ──►  Net Take-Home Pay & Line Items
 └──────────────────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────┐
 │ Stage 2 & 3: Tri-Vector Normalization    │  ──►  Nominal USD, PPP Int$, COL-Adjusted USD
 └──────────────────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────┐
 │ Stage 4: Market Percentile & Scoring     │  ──►  Market Percentile & 0-100 Equivalence Score
 └──────────────────────────────────────────┘
                      │
                      ▼
 [ Parity Matrix across SF, Bangalore, Berlin, Tokyo ]
```

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/shyamalpandey019-beep/Compensation-Equivalence.git
cd Compensation-Equivalence
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Launch the Web Application

```bash
streamlit run src/app.py
```

### 3. Run the CLI Tool

```bash
# Basic Analysis
python -m src.cli --gross 3500000 --country IN --city Bangalore --role "Software Engineer"

# With Cross-Border Parity Matrix
python -m src.cli --gross 140000 --country US --city "San Francisco" --parity

# Structured JSON Output (For CI/CD or Scripting)
python -m src.cli --gross 85000 --country DE --city Berlin --json
```

### 4. Run the REST API

```bash
uvicorn src.api:app --reload --port 8000
```

#### Sample API Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "gross_salary": 3500000,
    "country_code": "IN",
    "city_name": "Bangalore",
    "role": "Software Engineer",
    "include_parity": true
  }'
```

---

## 🧪 Testing & Validation

Run the complete test suite (21 unit and integration tests):

```bash
pytest -v
```

---

## 📚 Data Sources & References

- **World Bank Development Indicators**: International Comparison Program Purchasing Power Parity (`PA.NUS.PPP`)
- **Statutory Tax Tables (2024)**: India Income Tax Act (New Regime), IRS Federal 2024 Brackets, German Einkommensteuergesetz (§32a EStG), Japan National Tax Agency (NTA).
- **Cost of Living Matrix**: Numbeo Mid-2024 International City Indices (New York City Base 100.0).
