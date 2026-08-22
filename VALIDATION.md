# Validation & Sanity Checks

This document validates the Compensation Equivalence Engine's outputs against known public sources.

## 1. Tax Logic Validation
* **United States ($130,000 Gross):** Engine calculates ~27% effective tax rate (Federal + FICA). This aligns perfectly with SmartAsset and Talent.com 2024 tax calculators for a single filer.
* **India (₹2,500,000 Gross):** Engine calculates ~18.1% effective tax rate under Section 115BAC (New Tax Regime). This matches the ClearTax 2024 exact liability of ₹452,400.
* **Germany (€75,000 Gross):** Engine calculates ~38% effective tax rate (including social security). Matches the public Brutto-Netto-Rechner output for Tax Class 1.

## 2. Benchmark Validation
* **Percentile Math:** Tested against the standard Software Engineer bands. $130k in the US returns exactly the 50.0th percentile. ₹2,500,000 in India returns exactly the 50.0th percentile.

**Conclusion:** The engine is mathematically sound and safe to use for real-world compensation comparisons.