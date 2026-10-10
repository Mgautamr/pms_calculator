import sys
from pathlib import Path

# Make the project root importable (so `engine` and `app` can be found).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from app.formatting import format_inr, format_pct
from engine.fees import simulate

st.set_page_config(page_title="PMS Fee Calculator", page_icon="₹", layout="wide")

# ---------- presets (values are in percent) ----------
PRESETS = {
    "Custom": None,
    "Fixed fee only": dict(fixed=2.5, perf=0.0, hurdle=0.0, catch_up=False, hwm=False, exit=0.0),
    "Hybrid (fixed + profit share)": dict(fixed=1.5, perf=20.0, hurdle=0.0, catch_up=False, hwm=False, exit=0.0),
    "Hurdle, no catch-up": dict(fixed=0.0, perf=20.0, hurdle=10.0, catch_up=False, hwm=False, exit=0.0),
    "Hurdle with catch-up": dict(fixed=0.0, perf=20.0, hurdle=10.0, catch_up=True, hwm=False, exit=0.0),
    "High-water mark": dict(fixed=0.0, perf=20.0, hurdle=0.0, catch_up=False, hwm=True, exit=0.0),
    "Hurdle + high-water mark": dict(fixed=1.0, perf=20.0, hurdle=8.0, catch_up=False, hwm=True, exit=0.0),
}
DEFAULTS = PRESETS["Hybrid (fixed + profit share)"]
for key, val in DEFAULTS.items():
    st.session_state.setdefault(key, val)


def apply_preset():
    preset = PRESETS[st.session_state["preset"]]
    if preset:
        for key, val in preset.items():
            st.session_state[key] = val


# ---------- sidebar inputs ----------
with st.sidebar:
    st.header("Inputs")
    initial = st.number_input("Initial investment (₹)", min_value=100_000,
                              value=5_000_000, step=100_000)
    st.caption(format_inr(initial))
    years = st.slider("Years", 1, 10, 5)

    mode = st.radio("Gross returns", ["Same every year", "Different each year"])
    if mode == "Same every year":
        flat = st.number_input("Gross return per year (%)", min_value=-90.0,
                               value=12.0, step=0.5, format="%.2f")
        returns = [flat / 100] * years
    else:
        returns = [
            st.number_input(f"Year {i + 1} return (%)", min_value=-90.0,
                            value=12.0, step=0.5, format="%.2f", key=f"ret_{i}") / 100
            for i in range(years)
        ]

    st.subheader("Fee structure")
    st.selectbox("Start from a preset", list(PRESETS), key="preset", on_change=apply_preset)
    fixed = st.number_input("Fixed fee (% of opening value)", min_value=0.0,
                            max_value=10.0, step=0.25, key="fixed")
    perf = st.number_input("Performance fee (% of profit)", min_value=0.0,
                           max_value=50.0, step=1.0, key="perf")
    hurdle = st.number_input("Hurdle rate (%)", min_value=0.0,
                             max_value=30.0, step=0.5, key="hurdle")
    catch_up = st.checkbox("Catch-up", key="catch_up")
    hwm = st.checkbox("High-water mark", key="hwm")
    exit_load = st.number_input("Exit load (% of final value)", min_value=0.0,
                                max_value=5.0, step=0.25, key="exit")


# ---------- calculations ----------
def run(fixed_pct, perf_pct, hurdle_pct, catch_up_flag, hwm_flag, exit_pct):
    return simulate(initial, returns, fixed_pct / 100, perf_pct / 100,
                    hurdle_pct / 100, catch_up_flag, hwm_flag, exit_pct / 100)


def cagr(final_value):
    if final_value <= 0:
        return None
    return (final_value / initial) ** (1 / years) - 1


def pct_or_na(value):
    return "n/a" if value is None else format_pct(value)


result = run(fixed, perf, hurdle, catch_up, hwm, exit_load)

gross_path = [initial]
for r in returns:
    gross_path.append(gross_path[-1] * (1 + r))
gross_final = gross_path[-1]
net_path = [initial] + result["closing_values"]

gross_cagr = cagr(gross_final)
net_cagr = cagr(result["final_net_value"])
drag = None if net_cagr is None else gross_cagr - net_cagr

# ---------- page ----------
st.title("PMS Fee Calculator")
st.caption("See what an investor keeps after fees, for the same gross returns.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Final net value", format_inr(result["final_net_value"]),
          delta=f"{format_inr(result['final_net_value'] - gross_final)} vs no fees")
c2.metric("Total fees paid", format_inr(result["total_fees"]))
c3.metric("Net CAGR", pct_or_na(net_cagr),
          delta=None if drag is None else f"{-drag * 100:.2f} pts vs gross {pct_or_na(gross_cagr)}")
c4.metric("Fee drag per year", "n/a" if drag is None else f"{drag * 100:.2f} pts")

tab_year, tab_compare, tab_rules = st.tabs(["Year by year", "Compare fee models", "Rules used"])

with tab_year:
    rows, opening = [], initial
    for i in range(years):
        closing = result["closing_values"][i]
        rows.append({
            "Year": i + 1,
            "Gross return": format_pct(returns[i]),
            "Opening value": format_inr(opening),
            "Fixed fee": format_inr(result["fixed_fees"][i]),
            "Performance fee": format_inr(result["perf_fees"][i]),
            "Closing value": format_inr(closing),
        })
        opening = closing
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    if result["exit_amount"] > 0:
        st.write(f"Exit load on final value: **{format_inr(result['exit_amount'])}**")

    chart = pd.DataFrame({"No fees": gross_path, "After fees": net_path},
                         index=pd.Index(range(years + 1), name="Year"))
    st.line_chart(chart)
    st.caption("Chart shows portfolio value at each year end, before any exit load.")

with tab_compare:
    st.write("Same gross returns, your fixed fee, profit share, hurdle and exit load. "
             "Only the fee structure changes.")
    if hurdle == 0:
        st.info("Your hurdle is 0%, so several structures give similar answers. "
                "Set a hurdle above 0% in the sidebar to see them separate.")
    models = [
        ("Fixed fee only", dict(perf_pct=0.0, hurdle_pct=0.0, catch_up_flag=False, hwm_flag=False)),
        ("Hybrid (fixed + profit share)", dict(perf_pct=perf, hurdle_pct=0.0, catch_up_flag=False, hwm_flag=False)),
        ("Hurdle, no catch-up", dict(perf_pct=perf, hurdle_pct=hurdle, catch_up_flag=False, hwm_flag=False)),
        ("Hurdle with catch-up", dict(perf_pct=perf, hurdle_pct=hurdle, catch_up_flag=True, hwm_flag=False)),
        ("High-water mark", dict(perf_pct=perf, hurdle_pct=0.0, catch_up_flag=False, hwm_flag=True)),
        ("Hurdle + high-water mark", dict(perf_pct=perf, hurdle_pct=hurdle, catch_up_flag=False, hwm_flag=True)),
    ]
    table, fees_paid = [], {}
    for name, params in models:
        res = run(fixed, exit_pct=exit_load, **params)
        n_cagr = cagr(res["final_net_value"])
        table.append({
            "Fee structure": name,
            "Final net value": format_inr(res["final_net_value"]),
            "Total fees": format_inr(res["total_fees"]),
            "Net CAGR": pct_or_na(n_cagr),
            "Fee drag": "n/a" if n_cagr is None else f"{(gross_cagr - n_cagr) * 100:.2f} pts",
        })
        fees_paid[name] = res["total_fees"]
    st.dataframe(pd.DataFrame(table), hide_index=True)
    st.bar_chart(pd.Series(fees_paid, name="Total fees (₹)"))

with tab_rules:
    st.markdown(
        """
- Annual periods. Fees are charged at year end. No money is added or withdrawn.
- **Fixed fee** is a % of the opening value and is charged even in loss years.
- **Performance fee** is charged on profit after the fixed fee, measured against a base:
  the opening value, or the **high-water mark** (highest year-end value so far) if it is on.
- **Hurdle:** only profit above base × hurdle rate is charged. With **catch-up**, once profit
  clears the hurdle the fee applies to the whole profit.
- **Exit load** is charged once, on the final value.
- CAGR = (final value ÷ initial investment)^(1 ÷ years) − 1. Fee drag = gross CAGR − net CAGR.
"""
    )

st.divider()
st.caption("Educational illustration only. Not investment advice. Returns and fees are "
           "assumptions you enter, not real fund data or any manager's actual terms.")
