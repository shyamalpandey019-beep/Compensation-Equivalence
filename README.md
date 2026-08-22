# comp-equivalence-engine

Cross-country compensation equivalence engine. Given a salary + role + country,
outputs three **separate** adjusted figures — nominal FX, PPP-adjusted, and
cost-of-living-adjusted — plus a transparent weighted ranking across countries.

## Scope

- **Countries**: India (IN), Japan (JP), Germany (DE), United States (US)
- **Roles**: data scientist / data engineer, 1 general benchmark tier
- **No ML model** for scoring — weighted linear scoring, weights are user-adjustable
  and logged, not learned. The point is a defensible methodology, not a black box.

## Why three separate numbers, not one

- **Nominal FX**: literal currency conversion at a snapshot rate. Tells you what
  the number looks like in another currency, nothing about what it buys.
- **PPP-adjusted**: World Bank PPP conversion factor. Normalizes for the price of
  a national basket of goods. Answers "what does this income buy at home."
- **COL-adjusted**: city-level cost-of-living index (Numbeo baseline). Answers
  "what does this income buy in this specific city," which PPP does not capture
  (PPP is national-average, COL indices are city-level).

Collapsing these into one blended "adjusted salary" is the single most common
mistake in DIY versions of this project. This repo keeps them as three labeled
fields end to end — ingestion through API response.

## Repo layout

```
data/
  raw/          # unmodified API pulls, timestamped
  processed/    # cleaned/normalized versions
  reference/    # pinned, versioned config: tax brackets, PPP factors, COL index
src/
  ingest/       # PPP (World Bank), FX (Frankfurter), tax bracket loader
  tax/          # gross -> net tax calculators per country
  normalize/    # nominal / PPP / COL adjustment logic
  scoring/      # weighted ranking model
  api/          # FastAPI service
tests/
```

## Reproducibility rule

Every output carries the tax year, PPP year, and FX snapshot date it was computed
with. See `data/reference/SOURCES.md`. No live-only numbers — if a source can't
be pinned to a dated snapshot, it doesn't go in `reference/`.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Build log

- **Day 1**: repo scaffold, PPP ingestion (World Bank API), FX snapshot ingestion
(Frankfurter API), tax bracket reference data for IN/JP/DE/US (sourced, tax-year pinned).
- **Day 2**: Gross-to-net tax engine for IN/JP/DE/US, resolved statutory deduction & continuous formula
blockers (Germany §32a EStG, Japan NTA tiers, US Federal + FICA), automated unit test suite with pytest.
- **Day 3**: Built normalization layer separating Nominal USD, PPP Int$, and city-level Cost of Living (COL) purchasing power adjustments across 20 benchmark metropolitan hubs (IN, US, DE, JP); verified via automated pytest suite.
- **Day 4**: Built the `src/pipeline.py` orchestrator to route data across modules. Developed the `src/cli.py` tool using `argparse` for end-to-end terminal execution and reporting across 20 global tech hubs.
**Day 5**: Implemented an interactive Streamlit web dashboard for real-time visualization of cross-border compensation metrics using Pandas bar charts.