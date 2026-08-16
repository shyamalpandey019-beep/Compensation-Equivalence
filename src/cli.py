# src/cli.py
import argparse
import sys
from src.pipeline import run_pipeline

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compensation Equivalence Engine: Compare cross-border compensation with tax and normalization models."
    )
    parser.add_argument(
        "--gross",
        type=float,
        required=True,
        help="Gross annual salary in local currency (e.g., 2500000 for INR, 120000 for USD)",
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

    args = parser.parse_args()

    try:
        results = run_pipeline(args.gross, args.country, args.city)
    except Exception as e:
        print(f"Error executing pipeline: {e}", file=sys.stderr)
        sys.exit(1)

    inp = results["input"]
    tax = results["tax"]
    norm = results["normalized"]
    meta = results["metadata"]

    print("\n" + "=" * 60)
    print("       COMPENSATION EQUIVALENCE ENGINE REPORT       ")
    print("=" * 60)
    print(f"Input:        {inp['gross_salary']:,.2f} {inp['currency']} ({inp['city']}, {inp['country']})")
    print("-" * 60)
    print("TAX BREAKDOWN (Statutory 2024 Base):")
    print(f"  Net Pay:            {tax['net_local']:,.2f} {inp['currency']}")
    print(f"  Tax / Deductions:   {tax['tax_deducted']:,.2f} {inp['currency']}")
    print(f"  Effective Tax Rate: {tax['effective_tax_rate_pct']:.2f}%")
    print("-" * 60)
    print("NORMALIZED EQUIVALENCE METRICS:")
    print(f"  Nominal FX:         ${norm['nominal_usd']:,.2f} USD")
    print(f"  PPP Equivalence:    ${norm['ppp_int_dollars']:,.2f} Int$")
    print(f"  COL-Adjusted (NYC): ${norm['col_adjusted_usd']:,.2f} USD")
    print("-" * 60)
    print("METADATA & PROVENANCE:")
    print(f"  FX Snapshot Date:   {meta['fx_snapshot_date']}")
    print(f"  PPP Base Year:      {meta['ppp_indicator_year']}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()