# Data sources and known gaps

## Convention
- `data/reference/` holds curated, git-committed, dated snapshots. Nothing in
  here gets silently overwritten -- bump `retrieved_date` on any update.
- `data/raw/` holds regenerable API pulls (gitignored). Re-run `src/ingest/*.py`
  to refresh; never hand-edit.

## PPP conversion factors
- Source: World Bank API, indicator `PA.NUS.PPP` (PPP conversion factor, GDP,
  LCU per international $).
- Ingested via `src/ingest/ppp.py` -> `data/raw/ppp_raw.json`.
- Not yet pulled -- run the script locally (sandbox network is restricted to
  package registries, can't reach api.worldbank.org from here).

## FX snapshot
- Source: Frankfurter API (ECB reference rates), no key required.
- Ingested via `src/ingest/fx.py` -> `data/raw/fx_snapshot.json`.
- Same network restriction as above -- run locally.

## Tax brackets
- India: FY2025-26 new regime. Sourced 2026-08-06, see `tax_brackets.yaml` for
  URLs. Surcharge (>INR 50L) not yet modeled.
- Japan: 2025 national brackets confirmed. **Two open items block Day 2**:
  1. Employment income deduction formula not pinned (tiered, not flat).
  2. Basic deduction has a source conflict (JPY 480,000 vs JPY 950,000) --
     needs a direct NTA.go.jp check before the calculator can be trusted.
- Germany: 2025 zone boundaries confirmed, but zones 2-3 are smooth formulas
  under EStG section 32a, not flat rates. Day 1 pinned the boundaries only.
  Day 2 needs the exact formula coefficients or a validated piecewise-linear
  approximation with error bounds stated.

## Cost of living index
- Not sourced yet. Numbeo's programmatic API requires a paid contributor key;
  free tier does not reliably cover city-level COL index by API. Plan: either
  (a) pull spot values from Numbeo's public city pages manually, cited by URL
  and retrieval date, treated as a static reference table, or (b) substitute
  a fully free alternative if one is found. Decide at start of Day 2 -- don't
  let this block PPP/FX/tax work today.
