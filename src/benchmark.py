# src/benchmark.py
import json
from pathlib import Path

BENCHMARK_FILE = Path(__file__).resolve().parents[1] / "data" / "reference" / "benchmarks.json"

def calculate_percentile(salary: float, country_code: str) -> float:
    """
    Calculates the market percentile of a given salary using linear interpolation
    against standard P25, P50, and P75 compensation bands.
    """
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if country_code not in data:
        return 50.0  # Default to middle if data is missing

    bands = data[country_code]
    p25 = bands["p25"]
    p50 = bands["p50"]
    p75 = bands["p75"]

    # Linear interpolation to find the exact percentile
    if salary < p25:
        percentile = (salary / p25) * 25
    elif salary < p50:
        percentile = 25 + ((salary - p25) / (p50 - p25)) * 25
    elif salary < p75:
        percentile = 50 + ((salary - p50) / (p75 - p50)) * 25
    else:
        # Extrapolate above P75, capping at the 99.9th percentile
        percentile = 75 + ((salary - p75) / p75) * 24
        percentile = min(percentile, 99.9)

    return round(percentile, 1)