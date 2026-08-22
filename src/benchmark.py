# src/benchmark.py
import json
from pathlib import Path

BENCHMARK_FILE = Path(__file__).resolve().parents[1] / "data" / "reference" / "benchmarks.json"

def calculate_percentile(salary: float, country_code: str, role: str) -> float:
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Default to 50th percentile if data is missing for the country or role
    if country_code not in data or role not in data[country_code]:
        return 50.0  

    bands = data[country_code][role]
    p25, p50, p75 = bands["p25"], bands["p50"], bands["p75"]

    if salary < p25:
        percentile = (salary / p25) * 25
    elif salary < p50:
        percentile = 25 + ((salary - p25) / (p50 - p25)) * 25
    elif salary < p75:
        percentile = 50 + ((salary - p50) / (p75 - p50)) * 25
    else:
        percentile = 75 + ((salary - p75) / p75) * 24
        percentile = min(percentile, 99.9)

    return round(percentile, 1)