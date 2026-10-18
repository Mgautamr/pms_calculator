import html
import sys
from pathlib import Path

# Make the project root importable (so `engine` and `app` can be found).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from app import theme
from app.formatting import format_inr
from app.vehicles import (STATUS_ORDER, STATUS_SHORT, check_eligibility,
                          large_value_fund_note, load_data)

st.set_page_config(page_title="Compare PMS, MF, SIF and AIF", page_icon="₹", layout="wide")
theme.apply()


@st.cache_data
def get_data():
    return load_data()


data = get_data()
meta = data["meta"]
vehicles = data["vehicles"]

SHORT_NAMES = {
    "mutual_fund": "Mutual fund",
    "sif": "SIF",
    "pms": "PMS",
    "prim": "PMS mutual-fund route (PRIM, pending)",
    "aif": "AIF",
}


def dot(status):
    return theme.status_dot_html(status, STATUS_SHORT[status])


theme.masthead(
    "Compare PMS, mutual funds, SIFs and AIFs",
    f"Facts last verified {meta['last_verified']}. Every fact carries a dot showing how well it "
    "was verified, and a link to its source in the Sources tab.")
theme.notice("Open items", items=meta["open_items"])
st.markdown(theme.legend_html([(s, STATUS_SHORT[s]) for s in STATUS_ORDER]), unsafe_allow_html=True)

tab_compare, tab_access, tab_sources = st.tabs(
    ["Comparison", "Which can I access?", "Sources and gaps"])

# ---------- tab 1: comparison table ----------
ROWS = [
    ("Regulator", lambda v: v["regulator"]),
    ("Rulebook", lambda v: v["regulation"]),
    ("Minimum investment", ["min_investment"]),
    ("What it is", ["structure", "categories"]),
    ("Fees", ["fees"]),
    ("Tax", ["tax", "equity_oriented", "tax_cat3_effective"]),
    ("Tenure and liquidity", ["lock_in", "liquidity"]),
    ("Accredited investor rules", ["accredited_investor", "large_value_fund"]),
]


def table_cell(vehicle, spec):
    if callable(spec):
        return spec(vehicle)
    parts = []
    for key in spec:
        fact = vehicle["facts"].get(key)
        if fact:
            parts.append(theme.esc(fact["value"]) + " " + dot(fact["status"]))
    return theme.Html(" ".join(parts)) if parts else "–"


with tab_compare:
    ids = list(vehicles)
    headers = [""] + [SHORT_NAMES.get(i, vehicles[i]["name"]) for i in ids]
    rows = [[label] + [table_cell(vehicles[i], spec) for i in ids] for label, spec in ROWS]
    theme.data_table(headers, rows, min_width=1000)

# ---------- tab 2: eligibility ----------
with tab_access:
    theme.section("Which of these could you access?",
                  "Enter an amount to check it against each stated minimum.")
    col_a, col_b = st.columns([2, 1])
    amount = col_a.number_input("Amount you could invest (₹)", min_value=0,
                                value=5_000_000, step=100_000)
    col_a.caption(format_inr(amount))
    accredited = col_b.checkbox("I hold a SEBI accredited investor certificate")

    rows = []
    for r in check_eligibility(data, amount, accredited):
        is_open = r["verdict"] == "open"
        rows.append({
            "name": SHORT_NAMES.get(r["id"], r["name"]),
            "verdict": "open" if is_open else "below",
            "verdict_text": "Open to you" if is_open else "Below the minimum",
            "detail": theme.Html(theme.esc(r["detail"]) + " " + dot(r["figure_status"])),
            "caution": r["caution"],
        })
    st.markdown(theme.verdict_rows_html(rows), unsafe_allow_html=True)

    note = large_value_fund_note(data, amount, accredited)
    if note:
        theme.notice("Also open to you", text=note)

    st.caption("Meeting a minimum does not mean a product suits you, or that you meet its other "
               "conditions (KYC, residency, strategy risk). Check each offer document.")

# ---------- tab 3: sources ----------
with tab_sources:
    counts = {s: 0 for s in STATUS_ORDER}
    for v in vehicles.values():
        for f in v["facts"].values():
            counts[f["status"]] += 1
    st.markdown(theme.legend_html([(s, f"{STATUS_SHORT[s]}: {n}") for s, n in counts.items() if n]),
                unsafe_allow_html=True)

    for vid, v in vehicles.items():
        with st.expander(SHORT_NAMES.get(vid, v["name"])):
            st.markdown(f"**Regulator:** {v['regulator']}  \n**Rulebook:** {v['regulation']}")
            for fact in v["facts"].values():
                st.markdown(f"**{html.escape(fact['label'])}** {dot(fact['status'])} "
                            f"<span class='pms-muted'>{html.escape(STATUS_SHORT[fact['status']])}</span>",
                            unsafe_allow_html=True)
                st.write(fact["value"])
                if fact.get("note"):
                    st.caption(fact["note"])
                if fact["sources"]:
                    for s in fact["sources"]:
                        st.markdown(f"- [{s['supports']}]({s['url']})")
                else:
                    st.caption("No source found.")

theme.footnote("Educational illustration only, not investment advice. Rules and rates change; "
               "confirm with the regulator or a registered adviser before acting.")
