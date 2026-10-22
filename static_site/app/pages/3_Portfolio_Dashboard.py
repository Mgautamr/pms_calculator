import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Make the project root importable (so `engine` and `app` can be found).
sys.path.insert(0, str(ROOT))

import altair as alt
import pandas as pd
import streamlit as st

from app import theme
from app.formatting import format_pct
from app.portfolio_io import DataError, align, infer_periods_per_year, parse_series, rebase
from engine.analytics import drawdown_series, summarize

st.set_page_config(page_title="Portfolio dashboard", page_icon="₹", layout="wide")
theme.apply()

SAMPLE_PORTFOLIO = ROOT / "data" / "sample_portfolio.csv"
SAMPLE_BENCHMARK = ROOT / "data" / "sample_benchmark.csv"
FREQUENCY = {252: "daily", 52: "weekly", 12: "monthly", 4: "quarterly", 1: "yearly"}

theme.masthead(
    "Portfolio dashboard",
    "Upload a portfolio's value history to see how fast it grew, how bumpy the ride was and "
    "how deep its worst fall went. Add a benchmark to compare.")

# ---------- sidebar ----------
with st.sidebar:
    st.header("Your data")
    uploaded_portfolio = st.file_uploader("Portfolio values (CSV)", type="csv")
    uploaded_benchmark = st.file_uploader("Benchmark values (CSV, optional)", type="csv")
    risk_free_pct = st.number_input("Risk-free rate (% a year)", min_value=0.0, max_value=20.0,
                                    value=6.0, step=0.25)
    st.caption("An assumption you set. It is only used for the Sharpe ratio.")
    with st.expander("CSV format"):
        st.markdown(
            "Two columns with a header row: `date,value`.\n\n"
            "- Dates as `YYYY-MM-DD` or `DD-MM-YYYY`.\n"
            "- Values are portfolio value or NAV, all above zero.\n"
            "- One row per date, at least 3 rows.\n"
            "- Daily, weekly, monthly or quarterly data all work.")
    st.download_button("Download CSV template", data=SAMPLE_PORTFOLIO.read_text(encoding="utf-8"),
                       file_name="portfolio_template.csv", mime="text/csv")

# ---------- load and validate ----------
using_sample = uploaded_portfolio is None
portfolio_source = SAMPLE_PORTFOLIO if using_sample else uploaded_portfolio
if uploaded_benchmark is not None:
    benchmark_source = uploaded_benchmark
else:
    benchmark_source = SAMPLE_BENCHMARK if using_sample else None

try:
    portfolio = parse_series(portfolio_source)
except DataError as err:
    theme.notice("The portfolio file can't be used yet", text=str(err))
    st.stop()

benchmark = None
if benchmark_source is not None:
    try:
        benchmark = parse_series(benchmark_source)
        portfolio, benchmark = align(portfolio, benchmark)
    except DataError as err:
        theme.notice("The benchmark file can't be used yet", text=str(err))
        st.stop()

dates = [d.date() for d in portfolio["date"]]
periods = infer_periods_per_year(portfolio["date"])
risk_free = risk_free_pct / 100

try:
    mine = summarize(dates, list(portfolio["value"]), risk_free, periods)
    theirs = summarize(dates, list(benchmark["value"]), risk_free, periods) if benchmark is not None else None
except ValueError as err:
    theme.notice("The measures can't be calculated", text=str(err))
    st.stop()

if using_sample:
    theme.notice("Showing sample data",
                 text="This is synthetic data, not a real portfolio or fund. "
                      "Upload your own CSV in the sidebar to replace it.")

# ---------- headline figures ----------
cagr_note = vol_note = dd_note = sharpe_note = None
cagr_tone = "neutral"
if theirs:
    gap = mine["cagr"] - theirs["cagr"]
    cagr_note = f"{gap * 100:+.1f} pts against the benchmark's {format_pct(theirs['cagr'])}"
    cagr_tone = "good" if gap >= 0 else "bad"
    vol_note = f"Benchmark {format_pct(theirs['volatility'])}"
    dd_note = f"Benchmark {format_pct(theirs['max_drawdown'])}"
    sharpe_note = f"Benchmark {theirs['sharpe']:.2f}"
else:
    sharpe_note = f"At a {risk_free_pct:.2f}% risk-free rate"

theme.stat_strip([
    {"label": "Annual return (CAGR)", "value": format_pct(mine["cagr"]), "note": cagr_note, "tone": cagr_tone},
    {"label": "Volatility a year", "value": format_pct(mine["volatility"]), "note": vol_note},
    {"label": "Deepest fall from a peak", "value": format_pct(mine["max_drawdown"]), "note": dd_note},
    {"label": "Sharpe ratio", "value": f"{mine['sharpe']:.2f}", "note": sharpe_note},
])
st.caption(f"{len(portfolio)} {FREQUENCY[periods]} values from {dates[0]:%d %b %Y} to {dates[-1]:%d %b %Y}"
           + (", on the dates shared with the benchmark." if benchmark is not None else "."))

# ---------- growth chart ----------
theme.section("Growth of 100", "Both series are rebased to 100 on the first date, so they start level.")
names = ["Your portfolio"] + (["Benchmark"] if benchmark is not None else [])
frames = [pd.DataFrame({"Date": portfolio["date"], "Series": "Your portfolio",
                        "Value": rebase(list(portfolio["value"]))})]
if benchmark is not None:
    frames.append(pd.DataFrame({"Date": benchmark["date"], "Series": "Benchmark",
                                "Value": rebase(list(benchmark["value"]))}))
growth = alt.Chart(pd.concat(frames)).mark_line(strokeWidth=2.6).encode(
    x=alt.X("Date:T", title=None),
    y=alt.Y("Value:Q", title="Value of 100 invested", scale=alt.Scale(zero=False)),
    color=alt.Color("Series:N", scale=alt.Scale(domain=names, range=[theme.INK, theme.SLATE][:len(names)]),
                    legend=alt.Legend(orient="top", title=None)),
    tooltip=[alt.Tooltip("Date:T", format="%d %b %Y"), "Series:N", alt.Tooltip("Value:Q", format=".1f")],
).properties(height=340)
theme.show_chart(growth)

# ---------- drawdown chart ----------
theme.section("Falls from the peak",
              "How far your portfolio sat below its highest earlier value, at each date.")
dd = pd.DataFrame({"Date": portfolio["date"], "Drawdown": drawdown_series(list(portfolio["value"]))})
drawdown = alt.Chart(dd).mark_area(color=theme.BRICK, opacity=0.28,
                                   line={"color": theme.BRICK, "strokeWidth": 1.6}).encode(
    x=alt.X("Date:T", title=None),
    y=alt.Y("Drawdown:Q", title="Below previous peak", axis=alt.Axis(format="%")),
    tooltip=[alt.Tooltip("Date:T", format="%d %b %Y"), alt.Tooltip("Drawdown:Q", format=".1%")],
).properties(height=220)
theme.show_chart(drawdown)

# ---------- side by side ----------
if theirs:
    theme.section("Side by side")
    theme.data_table(
        ["Measure", "Your portfolio", "Benchmark"],
        [
            ["Annual return (CAGR)", format_pct(mine["cagr"]), format_pct(theirs["cagr"])],
            ["Volatility a year", format_pct(mine["volatility"]), format_pct(theirs["volatility"])],
            ["Deepest fall from a peak", format_pct(mine["max_drawdown"]), format_pct(theirs["max_drawdown"])],
            ["Sharpe ratio", f"{mine['sharpe']:.2f}", f"{theirs['sharpe']:.2f}"],
        ],
        numeric_cols=(1, 2))

with st.expander("How these are calculated"):
    st.markdown(
        "- **CAGR:** (last value ÷ first value) raised to 1 ÷ years, minus 1. Years are the days "
        "between the first and last date, divided by 365.\n"
        "- **Volatility:** the sample standard deviation of period returns, scaled to a year by the "
        f"square root of the observations per year (here {periods}, worked out from your dates).\n"
        "- **Deepest fall:** the largest drop from a running peak to a later low.\n"
        "- **Sharpe ratio:** (CAGR − risk-free rate) ÷ annual volatility. The risk-free rate is the "
        "assumption in the sidebar.\n"
        "- These come from a value history only. Money added or withdrawn along the way would need "
        "dated cash flows (XIRR), which this page does not read.")

theme.footnote("Educational illustration only, not investment advice. Past performance does not "
               "predict future results. Figures are only as good as the data you upload.")
