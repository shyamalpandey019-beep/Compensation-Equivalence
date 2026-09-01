# Comp Engine Project Rules & Future Enhancement Roadmap

## 🎯 Project Scope & Architecture Principles
- **Project Identity**: `Comp Engine` (Global Compensation Normalization Engine).
- **Core Technology Stack**:
  - Frontend: Single-page Streamlit application embedding a Tailwind CSS design system canvas (`src/app.py`).
  - Backend Services: FastAPI (`src/api.py`) with Pydantic v2 schemas and CLI tool (`src/cli.py`).
  - Mathematical Engine: Progressive statutory tax modeling (`src/tax/calculator.py`), PPP/COL normalization (`src/normalize/adjust.py`), and piece-wise market benchmark percentiles (`src/benchmark.py`).
- **Design & UI Constraint**:
  - No authentication, login, or signup screens.
  - The native Streamlit sidebar and headers must remain completely hidden.
  - Interactive calculations should execute on explicit button click (e.g. `handleRecalculateClick()`), while input previews remain responsive.

---

## 🚀 Future Enhancement Roadmap (Pending Next Phases)

### Phase 1: Interactive Multi-Offer Canvas & Shareable State
- **Multi-Offer Side-by-Side Comparison**: Allow users/recruiters to compare 2–3 international offers simultaneously (e.g., US $150k vs DE €85k vs IN ₹40L) with visual delta indicators and runway bars.
- **Disposable Income & Savings Simulator**: Introduce discretionary spending and housing cost sliders (e.g., 1BR vs 3BR rent, healthcare out-of-pocket).
- **URL State Serialization (`/share?base=...`)**: Base64 or query-param URL serialization allowing users to share compensation calculations directly via URL.

### Phase 2: Granular Tax Engine & Level-Based Benchmarking
- **US Sub-National State & Municipal Taxes**:
  - Support California (9.3%), New York State & NYC (+3.876%), Washington (0%), Texas (0%).
- **International Surcharges & Social Contributions**:
  - Germany: Church tax (*Kirchensteuer* 8–9%) and statutory health insurance caps (*Krankenkasse*).
  - Japan: Inhabitant residence tax (*Jūminzei* 10%).
- **Seniority Levels**:
  - Expand role benchmarks from generic titles to discrete bands: `Junior (L3)`, `Mid-Level (L4)`, `Senior (L5)`, `Staff / Lead (L6)`, `Principal (L7)`.

### Phase 3: Branded PDF Comp Summary Export
- **1-Click Executive PDF Generation**:
  - Export a branded, high-fidelity 1-page PDF summary sheet (including gross-to-net waterfall, purchasing power equivalences, and parity matrix) suitable for candidate offer packages.

### Phase 4: Automated Economic Telemetry & Integrations
- **Scheduled Ingestion Pipeline**: GitHub Actions cron job (`0 0 1 * *`) for automated monthly updates from European Central Bank FX rates and World Bank PPP indices.
- **Equity / RSU Modeling**: Cross-border tax models for RSUs and stock options (vesting vs capital gains tax).
- **Integrations & Bot**: Slack slash command (`/comp`) and ATS webhook triggers (Greenhouse, Ashby, Deel).
