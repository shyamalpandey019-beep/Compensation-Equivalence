# Methodology: Compensation Equivalence Engine

This document explains the mathematical pipeline used to compare cross-border compensation. The engine normalizes gross salaries across different tax regimes, purchasing power parities (PPP), and local market percentiles.

## 1. Statutory Tax Deduction
Before we can compare salaries, we must calculate the actual take-home pay. 
* **Input:** Gross Salary in Local Currency.
* **Process:** The engine processes the gross salary through a country-specific statutory tax bracket model (updated for 2024). This includes federal/national income tax, state/local taxes (e.g., US California/New York, German Solidarity Surcharge), and mandatory social security contributions.
* **Output:** Net Local Take-Home Pay.

## 2. Currency & Purchasing Power Normalization
Comparing a US Dollar to an Indian Rupee directly is flawed. We use a three-step normalization process on the **Net Pay**:
* **Nominal USD:** Converted using real-time foreign exchange (FX) market rates. 
* **Purchasing Power Parity (Int$):** Converted using World Bank PPP Conversion Factors. This answers: *How much standard global goods can this salary buy?*
* **Cost of Living (COL) Adjusted USD:** We use the Numbeo COL Index, anchoring New York City at 100.0. This scales the nominal value based on local rent, groceries, and services in specific tech hubs (e.g., SF, Berlin, Bangalore).

## 3. Market Benchmarking
We map the gross salary against real-world tech compensation bands (Entry P25, Median P50, Senior P75) for a standard "Software Engineer" using linear interpolation. This determines the salary's percentile rank in its specific local market.

## 4. The Unified Equivalence Score (0-100)
To provide a single comparable metric, the engine calculates a final weighted score:
* **50% Weight:** Local Market Percentile (How competitive is the pay locally?)
* **50% Weight:** Global Purchasing Power (How much absolute wealth does this provide, capped at $100k COL-Adjusted USD for scaling?)