# src/validate.py
import sys
from pathlib import Path

# Path resolution fix so we can run this from anywhere
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.pipeline import run_pipeline

# 3 Real-World Salary Scenarios from public data
scenarios = [
    {"gross": 130000, "country": "US", "city": "San Francisco", "source": "Levels.fyi Median SWE"},
    {"gross": 2500000, "country": "IN", "city": "Bangalore", "source": "Glassdoor Median SWE"},
    {"gross": 75000, "country": "DE", "city": "Berlin", "source": "StepStone Median SWE"}
]

print("==================================================")
print(" DAY 6: SANITY CHECK AGAINST PUBLIC SOURCES")
print("==================================================\n")

for s in scenarios:
    res = run_pipeline(s["gross"], s["country"], s["city"])
    tax = res["tax"]
    norm = res["normalized"]
    bench = res["benchmark"]
    
    print(f"Scenario: {s['gross']:,} {res['input']['currency']} in {s['city']} ({s['source']})")
    print(f" -> Effective Tax Rate: {tax['effective_tax_rate_pct']}% (Verify vs Talent.com / ClearTax)")
    print(f" -> Market Percentile:  {bench['percentile']}th (Verify vs Levels.fyi)")
    print(f" -> COL-Adjusted USD:   ${norm['col_adjusted_usd']:,} (Verify vs Numbeo)")
    print(f" -> Overall Score:      {bench['overall_score_out_of_100']}/100")
    print("-" * 50)