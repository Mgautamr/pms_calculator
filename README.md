---
title: PMS Toolkit
emoji: 📈
colorFrom: red
colorTo: gray
sdk: streamlit
sdk_version: 1.65.0
python_version: "3.12"
app_file: app/streamlit_app.py
pinned: false
---

# PMS toolkit

An educational toolkit for understanding Portfolio Management Services (PMS) in India: what they cost, how they compare with other ways to invest, and how a portfolio has performed.

**Educational only. Not investment advice.** Every return and fee is an assumption you enter, or synthetic sample data. Nothing here is a real fund, a real manager's terms, or a recommendation.

## What is in it

- **Fee calculator.** Runs the same gross returns through fixed, hybrid, hurdle (with and without catch-up), high-water-mark and combined fee structures, and shows what the investor keeps, the total fees paid and the fee drag on the annual return.
- **Compare vehicles.** PMS, mutual funds, SIFs and AIFs side by side. Every fact carries a source link and a label for how well it was verified (official source, official text via a database, secondary source, or not verified). Facts that could not be verified are shown as such, not guessed.
- **Portfolio dashboard.** Upload a CSV of dates and values (and optionally a benchmark) to see annual return (CAGR), volatility, deepest fall from a peak and Sharpe ratio. It opens on synthetic sample data.

## How the numbers are checked

The fee engine (`engine/fees.py`) and the analytics (`engine/analytics.py`) are plain Python with no Streamlit code in them. Their results are tested against hand-built Excel workbooks in `tests/`, which act as the answer key. The conventions each model follows (when fees are charged, what the hurdle is measured against, how the high-water mark is tracked) are written out in the workbook and in the app's "Rules used" tab.

Facts in `data/vehicles.json` are dated (`last_verified`) and may go out of date. Rules and tax rates change; confirm with the regulator or a registered adviser before acting.

## Run it locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1      Mac/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
streamlit run app/streamlit_app.py
```

## Project layout

```
app/                 Streamlit pages, theme and the landing component
  pages/             Fee calculator, compare vehicles, portfolio dashboard
  landing_component/ The animated home screen (HTML and three.js)
engine/              Fee models and portfolio analytics (no UI code)
data/                vehicles.json (sourced facts) and sample CSVs (synthetic)
tests/               pytest suite and the Excel reference workbooks
```

## Limits

- The dashboard reads value histories only. Money added or withdrawn along the way would need dated cash flows (XIRR), which it does not read.
- Fee conventions are one reasonable reading of terms that vary between managers.
- The animated home screen loads three.js and fonts from public CDNs, so it needs an internet connection.
