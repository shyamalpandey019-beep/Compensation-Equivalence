# src/cli.py
import argparse
import json
import sys
from pathlib import Path

# Path resolution fix
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.pipeline import run_pipeline, calculate_parity_matrix

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Comp Engine CLI: Global Compensation Normalization, Statutory Tax, and Cross-Border Parity Engine."
    )
    parser.add_argument(
        "--gross",
        type=float,
        required=True,
        help="Gross annual salary in local currency (e.g., 3500000 for INR, 140000 for USD, 85000 for EUR)",
    )
    parser.add_argument(
        "--country",
        type=str,
        required=True,
        choices=["IN", "JP", "DE", "US"],
        help="2-letter ISO Country Code (IN, JP, DE, US)",
    )
    parser.add_argument(
        "--city",
        type=str,
        required=True,
        help="Metropolitan city name (e.g., Bangalore, Berlin, Tokyo, New York, San Francisco)",
    )
    parser.add_argument(
        "--role",
        type=str,
        default="Software Engineer",
        choices=["Software Engineer", "Data Scientist", "Data Analyst"],
        help="Job role for market percentile benchmarking",
    )
    parser.add_argument(
        "--parity",
        action="store_true",
        help="Include cross-border equivalent compensation matrix across SF, Bangalore, Berlin, Tokyo",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output raw JSON results for scripting and automated pipelines",
    )

    args = parser.parse_args()

    try:
        results = run_pipeline(
            gross_salary=args.gross,
            country_code=args.country,
            city_name=args.city,
            role=args.role,
            include_parity=args.parity
        )
    except Exception as e:
        print(f"Error executing pipeline: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(results, indent=2))
        return

    inp = results["input"]
    tax = results["tax"]
    norm = results["normalized"]
    bench = results["benchmark"]
    meta = results["metadata"]

    print("\n" + "=" * 68)
    print("           COMP ENGINE - GLOBAL COMPENSATION EQUIVALENCE REPORT        ")
    print("=" * 68)
    print(f"Position:     {bench['role']} in {inp['city']}, {inp['country']}")
    print(f"Gross Salary: {inp['gross_salary']:,.2f} {inp['currency']} / year")
    print("-" * 68)
    print("STATUTORY TAX BREAKDOWN (2024 Base):")
    print(f"  Net Annual Take-Home: {tax['net_local']:,.2f} {inp['currency']} ({tax['net_local']/12:,.2f} / month)")
    print(f"  Total Tax Burden:     {tax['tax_deducted']:,.2f} {inp['currency']}")
    print(f"  Effective Tax Rate:   {tax['effective_tax_rate_pct']:.2f}%")
    if tax.get("breakdown"):
        print("  Line Items:")
        for item in tax["breakdown"]:
            prefix = "    * "
            amt_str = f"{item['amount']:,.2f} {inp['currency']}"
            print(f"{prefix}{item['label']:<34} {amt_str:>18}  ({item.get('note', '')})")
    print("-" * 68)
    print("NORMALIZED PURCHASING POWER METRICS:")
    print(f"  Nominal USD (Live FX):     ${norm['nominal_usd']:,.2f} USD")
    print(f"  PPP Int$ (World Bank):     ${norm['ppp_int_dollars']:,.2f} Int$")
    print(f"  COL-Adjusted (NYC 100):    ${norm['col_adjusted_usd']:,.2f} USD")
    print("-" * 68)
    print("MARKET BENCHMARK & COHORT:")
    print(f"  Role Market Percentile:    {bench['percentile']}th percentile")
    print(f"  Equivalence Score:         {bench['overall_score_out_of_100']} / 100")
    print("-" * 68)
    print("DATA PROVENANCE:")
    print(f"  FX Snapshot Rate Date:     {meta.get('fx_snapshot_date')}")
    print(f"  PPP Indicator Year:        {meta.get('ppp_indicator_year')}")

    if args.parity and "parity_matrix" in results:
        print("=" * 68)
        print("       CROSS-BORDER PARITY MATRIX (EQUAL PURCHASING POWER)       ")
        print("=" * 68)
        print(f"{'Hub':<24} {'Req. Gross':<16} {'Net Pay':<16} {'Tax Rate':<10}")
        print("-" * 68)
        for hub in results["parity_matrix"]:
            gross_fmt = f"{hub['required_gross']:,.0f} {hub['currency']}"
            net_fmt = f"{hub['net_local']:,.0f} {hub['currency']}"
            tax_fmt = f"{hub['effective_tax_rate_pct']:.1f}%"
            print(f"{hub['hub']:<24} {gross_fmt:<16} {net_fmt:<16} {tax_fmt:<10}")

    print("=" * 68 + "\n")

if __name__ == "__main__":
    main()