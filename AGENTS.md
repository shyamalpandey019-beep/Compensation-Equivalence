# Comp Engine — Agent Instructions & Roadmap

## 📌 Project Overview
**Comp Engine** is a global compensation normalization engine translating tech salaries across jurisdictions (India, US, Germany, Japan) using 2024 progressive tax schedules, World Bank PPP factors, Numbeo Cost of Living indices, and local tech market benchmarks.

## 🎯 Architecture & UI Constraints
- **Brand Name**: Use **Comp Engine** everywhere (no references to previous names).
- **Frontend**: Streamlit in `src/app.py` embedding full Tailwind design canvas. Native Streamlit sidebars and headers must stay hidden.
- **Interactivity**: Input previews update live, but full equivalence metrics only recompute on explicit button clicks (`handleRecalculateClick`).
- **Tests**: Keep all unit & integration tests passing (`pytest -v`).

## 🗺️ Future Roadmap & Next Tasks (To Resume in Future Sessions)
1. **Multi-Offer Side-by-Side Comparison Canvas & Shareable URLs**:
   - Compare 2–3 international offers simultaneously with net disposable savings runway.
   - Support shareable URLs encoding calculation state.
2. **Sub-National State Taxes & Seniority Levels (L3–L6)**:
   - Add US State Taxes (California, New York/NYC, Texas, Washington).
   - Add Junior, Mid-Level, Senior, and Staff levels to market percentiles.
3. **1-Click Executive PDF Offer Summary Export**:
   - Export downloadable 1-page branded PDF compensation briefs for talent acquisition and candidates.
4. **Automated Monthly Economic Telemetry & Integrations**:
   - GitHub Actions monthly cron for ECB FX rates and World Bank PPP updates.
   - Slack bot (`/comp`) and RSU/equity taxation models.
