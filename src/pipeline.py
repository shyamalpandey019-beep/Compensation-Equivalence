# src/pipeline.py
import json
from pathlib import Path
from typing import Any, Dict, List

from src.tax.calculator import get_net_pay, get_tax_breakdown
from src.normalize.adjust import (
    calculate_nominal,
    calculate_ppp,
    calculate_col_adjusted,
    COL_DATA,
)
from src.benchmark import calculate_percentile
from src.score import calculate_score

BASE_DIR = Path(__file__).resolve().parents[1]
FX_PATH = BASE_DIR / "data" / "raw" / "fx_snapshot.json"
PPP_PATH = BASE_DIR / "data" / "raw" / "ppp_raw.json"

COUNTRY_ISO3_MAP = {
    "IN": "IND", "JP": "JPN", "DE": "DEU", "US": "USA",
}

COUNTRY_CURRENCY_MAP = {
    "IN": "INR", "JP": "JPY", "DE": "EUR", "US": "USD",
}

MAJOR_GLOBAL_HUBS = [
    {"country": "US", "city": "San Francisco", "label": "San Francisco, USA", "flag": "🇺🇸"},
    {"country": "IN", "city": "Bangalore", "label": "Bangalore, India", "flag": "🇮🇳"},
    {"country": "DE", "city": "Berlin", "label": "Berlin, Germany", "flag": "🇩🇪"},
    {"country": "JP", "city": "Tokyo", "label": "Tokyo, Japan", "flag": "🇯🇵"},
]


def load_raw_data() -> tuple[dict, dict]:
    with open(FX_PATH, "r", encoding="utf-8") as f:
        fx_data = json.load(f)
    with open(PPP_PATH, "r", encoding="utf-8") as f:
        ppp_data = json.load(f)
    return fx_data, ppp_data


def solve_gross_for_target_net(target_net_local: float, country_code: str) -> float:
    """
    Binary search solver to calculate the gross salary required in a jurisdiction
    to achieve an exact target net take-home pay under progressive tax schedules.
    """
    if target_net_local <= 0:
        return 0.0

    low = target_net_local
    high = target_net_local * 3.5

    for _ in range(35):
        mid = (low + high) / 2.0
        net = get_net_pay(mid, country_code)
        if net < target_net_local:
            low = mid
        else:
            high = mid

    return round((low + high) / 2.0, 2)


def calculate_parity_matrix(gross_salary: float, country_code: str, city_name: str) -> List[Dict[str, Any]]:
    """
    Calculates equivalent gross compensation required across major global hubs
    to deliver identical purchasing power (COL-adjusted NYC base).
    """
    country_code = country_code.upper()
    fx_data, _ = load_raw_data()
    currency = COUNTRY_CURRENCY_MAP.get(country_code, "USD")
    fx_rate = fx_data["rates"].get(currency, 1.0)

    # 1. Source net pay and COL-adjusted USD
    net_local = get_net_pay(gross_salary, country_code)
    nom_usd = calculate_nominal(net_local, fx_rate)
    source_col_usd = calculate_col_adjusted(nom_usd, country_code, city_name)

    parity_results = []
    for hub in MAJOR_GLOBAL_HUBS:
        tgt_country = hub["country"]
        tgt_city = hub["city"]
        tgt_curr = COUNTRY_CURRENCY_MAP.get(tgt_country, "USD")
        tgt_fx = fx_data["rates"].get(tgt_curr, 1.0)
        tgt_col = COL_DATA.get("cities", {}).get(tgt_country, {}).get(tgt_city, 100.0)

        # Target needed nominal USD and local net
        needed_nom_usd = source_col_usd / (100.0 / tgt_col)
        needed_net_local = needed_nom_usd * tgt_fx

        # Solve required gross
        tgt_gross = solve_gross_for_target_net(needed_net_local, tgt_country)
        tgt_net = get_net_pay(tgt_gross, tgt_country)
        tgt_tax = tgt_gross - tgt_net
        tgt_tax_rate = (tgt_tax / tgt_gross) * 100 if tgt_gross > 0 else 0.0

        parity_results.append({
            "hub": hub["label"],
            "flag": hub["flag"],
            "country": tgt_country,
            "city": tgt_city,
            "currency": tgt_curr,
            "required_gross": tgt_gross,
            "net_local": round(tgt_net, 2),
            "tax_deducted": round(tgt_tax, 2),
            "effective_tax_rate_pct": round(tgt_tax_rate, 2),
            "col_index": tgt_col,
            "nominal_usd_equivalent": round(tgt_gross / tgt_fx, 2),
        })

    return parity_results


def run_pipeline(
    gross_salary: float, 
    country_code: str, 
    city_name: str, 
    role: str = "Software Engineer",
    include_parity: bool = False
) -> Dict[str, Any]:
    country_code = country_code.upper()
    if country_code not in COUNTRY_CURRENCY_MAP:
        raise ValueError(f"Unsupported country code: {country_code}. Supported: {list(COUNTRY_CURRENCY_MAP.keys())}")

    fx_data, ppp_data = load_raw_data()
    currency = COUNTRY_CURRENCY_MAP.get(country_code)

    # 1. Tax calculation
    net_local = get_net_pay(gross_salary, country_code)
    tax_info = get_tax_breakdown(gross_salary, country_code)
    total_tax = gross_salary - net_local
    effective_tax_rate = (total_tax / gross_salary) * 100 if gross_salary > 0 else 0.0

    # 2. Extract FX and PPP Rates
    fx_rate = fx_data["rates"].get(currency, 1.0)
    iso3 = COUNTRY_ISO3_MAP.get(country_code)
    ppp_entry = ppp_data["latest_per_country"].get(iso3, {"value": 1.0, "year": 2024})
    ppp_factor = ppp_entry["value"]

    # 3. Normalization
    nominal_usd = calculate_nominal(net_local, fx_rate)
    ppp_int_usd = calculate_ppp(net_local, ppp_factor)
    col_adjusted_usd = calculate_col_adjusted(nominal_usd, country_code, city_name)

    # 4. Market Percentile Benchmark 
    market_percentile = calculate_percentile(gross_salary, country_code, role)
    
    # 5. Overall Weighted Score 
    comp_score = calculate_score(market_percentile, col_adjusted_usd)

    output: Dict[str, Any] = {
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
            "breakdown": tax_info.get("items", []),
        },
        "normalized": {
            "nominal_usd": round(nominal_usd, 2),
            "ppp_int_dollars": round(ppp_int_usd, 2),
            "col_adjusted_usd": round(col_adjusted_usd, 2),
        },
        "benchmark": {
            "role": role,
            "percentile": market_percentile,
            "overall_score_out_of_100": comp_score
        },
        "metadata": {
            "fx_snapshot_date": fx_data.get("rate_date"),
            "ppp_indicator_year": ppp_entry.get("year"),
        }
    }

    if include_parity:
        output["parity_matrix"] = calculate_parity_matrix(gross_salary, country_code, city_name)

    return output