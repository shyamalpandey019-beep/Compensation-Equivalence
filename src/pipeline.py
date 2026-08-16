# src/pipeline.py
import json
from pathlib import Path
from typing import Any, Dict

from src.tax.calculator import get_net_pay
from src.normalize.adjust import (
    calculate_nominal,
    calculate_ppp,
    calculate_col_adjusted,
)

BASE_DIR = Path(__file__).resolve().parents[1]
FX_PATH = BASE_DIR / "data" / "raw" / "fx_snapshot.json"
PPP_PATH = BASE_DIR / "data" / "raw" / "ppp_raw.json"

COUNTRY_ISO3_MAP = {
    "IN": "IND",
    "JP": "JPN",
    "DE": "DEU",
    "US": "USA",
}

COUNTRY_CURRENCY_MAP = {
    "IN": "INR",
    "JP": "JPY",
    "DE": "EUR",
    "US": "USD",
}

def load_raw_data() -> tuple[dict, dict]:
    """Loads FX and PPP snapshots from data/raw/."""
    if not FX_PATH.exists():
        raise FileNotFoundError(
            f"Missing FX snapshot at {FX_PATH}. Run 'python -m src.ingest.fx' first."
        )
    if not PPP_PATH.exists():
        raise FileNotFoundError(
            f"Missing PPP data at {PPP_PATH}. Run 'python -m src.ingest.ppp' first."
        )

    with open(FX_PATH, "r", encoding="utf-8") as f:
        fx_data = json.load(f)

    with open(PPP_PATH, "r", encoding="utf-8") as f:
        ppp_data = json.load(f)

    return fx_data, ppp_data

def run_pipeline(gross_salary: float, country_code: str, city_name: str) -> Dict[str, Any]:
    """
    Executes full compensation calculation:
    Gross -> Statutory Net -> Nominal USD -> PPP Int$ -> COL-Adjusted USD.
    """
    country_code = country_code.upper()
    fx_data, ppp_data = load_raw_data()

    currency = COUNTRY_CURRENCY_MAP.get(country_code)
    if not currency:
        raise ValueError(f"Unsupported country code: {country_code}")

    # 1. Tax calculation
    net_local = get_net_pay(gross_salary, country_code)
    total_tax = gross_salary - net_local
    effective_tax_rate = (total_tax / gross_salary) * 100 if gross_salary > 0 else 0.0

    # 2. FX rate extraction (1 USD = X Local Currency)
    fx_rate = fx_data["rates"].get(currency)
    if fx_rate is None:
        raise ValueError(f"FX rate not available for currency: {currency}")

    # 3. PPP conversion factor extraction
    iso3 = COUNTRY_ISO3_MAP.get(country_code)
    ppp_entry = ppp_data["latest_per_country"].get(iso3)
    if not ppp_entry:
        raise ValueError(f"PPP factor not available for ISO3 code: {iso3}")
    ppp_factor = ppp_entry["value"]

    # 4. Normalization calculations
    nominal_usd = calculate_nominal(net_local, fx_rate)
    ppp_int_usd = calculate_ppp(net_local, ppp_factor)
    col_adjusted_usd = calculate_col_adjusted(nominal_usd, country_code, city_name)

    return {
        "input": {
            "gross_salary": gross_salary,
            "country": country_code,
            "city": city_name,
            "currency": currency,
        },
        "tax": {
            "net_local": round(net_local, 2),
            "tax_deducted": round(total_tax, 2),
            "effective_tax_rate_pct": round(effective_tax_rate, 2),
        },
        "normalized": {
            "nominal_usd": round(nominal_usd, 2),
            "ppp_int_dollars": round(ppp_int_usd, 2),
            "col_adjusted_usd": round(col_adjusted_usd, 2),
        },
        "metadata": {
            "fx_snapshot_date": fx_data.get("rate_date"),
            "ppp_indicator_year": ppp_entry.get("year"),
        },
    }