"""
Pull PPP conversion factors from the World Bank API.

Indicator PA.NUS.PPP = PPP conversion factor, GDP (LCU per international $).
No API key required. Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

Usage:
    python -m src.ingest.ppp
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

COUNTRIES = ["IN", "JP", "DE", "US"]  # ISO 2-letter codes: India, Japan, Germany, United StatesINDICATOR = "PA.NUS.PPP"
BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
OUT_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "ppp_raw.json"


def fetch_ppp(countries: list[str] = COUNTRIES, start_year: int = 2018, end_year: int = 2024) -> list[dict]:
    """
    Fetch PPP conversion factors for the given countries and year range.
    Returns a flat list of {country, country_code, year, value} records,
    most recent year first per country. Raises on HTTP or malformed-response
    errors -- do not swallow, this feeds a financial calculation downstream.
    """
    url = BASE_URL.format(countries=";".join(countries), indicator=INDICATOR)
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 1000,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    # World Bank API returns [metadata, data] on success, or a single dict on error.
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        raise ValueError(f"Unexpected World Bank API response shape: {payload}")

    records = []
    for row in payload[1]:
        if row.get("value") is None:
            continue  # skip years with no reported figure rather than fabricate
        records.append(
            {
                "country": row["country"]["value"],
                "country_code": row["countryiso3code"],
                "year": int(row["date"]),
                "value": row["value"],
            }
        )
    return records


def latest_per_country(records: list[dict]) -> dict:
    """Reduce to the most recent non-null value per country."""
    latest: dict[str, dict] = {}
    for r in records:
        code = r["country_code"]
        if code not in latest or r["year"] > latest[code]["year"]:
            latest[code] = r
    return latest


def main() -> None:
    records = fetch_ppp()
    if not records:
        raise RuntimeError("World Bank API returned no PPP records -- check indicator code and country list")

    latest = latest_per_country(records)

    out = {
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "indicator": INDICATOR,
        "source": "World Bank API",
        "all_records": records,
        "latest_per_country": latest,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"Wrote {len(records)} records ({len(latest)} countries) to {OUT_PATH}")
    for code, rec in latest.items():
        print(f"  {code}: {rec['value']:.4f} LCU per international $ ({rec['year']})")


if __name__ == "__main__":
    main()
