"""
Pull a dated FX snapshot from the Frankfurter API (ECB reference rates).
No API key required. Docs: https://www.frankfurter.app/docs/

This is a SNAPSHOT, not a live feed -- the point of this project is a
reproducible comparison, not a real-time converter. Every output downstream
must carry the date this file was fetched.

Usage:
    python -m src.ingest.fx
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_CURRENCY = "USD"
TARGET_CURRENCIES = ["INR", "JPY", "EUR"]
URL = "https://api.frankfurter.app/latest"
OUT_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "fx_snapshot.json"


def fetch_fx(base: str = BASE_CURRENCY, targets: list[str] = TARGET_CURRENCIES) -> dict:
    params = {"from": base, "to": ",".join(targets)}
    resp = requests.get(URL, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    missing = set(targets) - set(payload.get("rates", {}))
    if missing:
        raise ValueError(f"Frankfurter API response missing rates for: {missing}")

    return payload


def main() -> None:
    payload = fetch_fx()

    out = {
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "rate_date": payload["date"],  # ECB reference date, may lag fetch date on weekends/holidays
        "base": payload["base"],
        "rates": payload["rates"],
        "source": "Frankfurter API (ECB reference rates)",
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"Wrote FX snapshot ({payload['date']}) to {OUT_PATH}")
    for ccy, rate in payload["rates"].items():
        print(f"  1 {payload['base']} = {rate} {ccy}")


if __name__ == "__main__":
    main()
