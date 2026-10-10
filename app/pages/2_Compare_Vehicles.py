import sys
from pathlib import Path

# Make the project root importable (so `engine` and `app` can be found).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from app.formatting import format_inr
from app.vehicles import (STATUS_EMOJI, STATUS_ORDER, STATUS_SHORT, check_eligibility,
                          large_value_fund_note, load_data)

st.set_page_config(page_title="Compare PMS, MF, SIF and AIF", page_icon="₹", layout="wide")


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


def badge(status):
    return STATUS_EMOJI[status]


st.title("Compare PMS, mutual funds, SIFs and AIFs")
st.caption(f"Facts last verified {meta['last_verified']}. Educational only, not investment advice.")

st.warning("**Open items:**\n" + "\n".join(f"- {item}" for item in meta["open_items"]))

legend = "  ".join(f"{badge(s)} {STATUS_SHORT[s]}" for s in STATUS_ORDER if s != "official_reported")
st.markdown(f"**How well each fact is verified:** {legend}")

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


def clean(text):
    return text.replace("|", "/").replace("\n", " ")


def table_cell(vehicle, spec):
    if callable(spec):
        return clean(spec(vehicle))
    parts = []
    for key in spec:
        fact = vehicle["facts"].get(key)
        if fact:
            parts.append(f"{clean(fact['value'])} {badge(fact['status'])}")
    return " ".join(parts) if parts else "–"


with tab_compare:
    ids = list(vehicles)
    header = "| |" + "|".join(f" **{SHORT_NAMES.get(i, vehicles[i]['name'])}** " for i in ids) + "|"
    divider = "|---|" + "|".join("---" for _ in ids) + "|"
    lines = [header, divider]
    for label, spec in ROWS:
        cells = " | ".join(table_cell(vehicles[i], spec) for i in ids)
        lines.append(f"| **{label}** | {cells} |")
    st.markdown("\n".join(lines))
    st.caption("A symbol after a fact shows how well that fact was verified. "
               "See the Sources tab for links, and for what could not be verified.")

# ---------- tab 2: eligibility ----------
with tab_access:
    st.write("Enter an amount to see which of these you could access, based on the stated minimums.")
    col_a, col_b = st.columns([2, 1])
    amount = col_a.number_input("Amount you could invest (₹)", min_value=0,
                                value=5_000_000, step=100_000)
    col_a.caption(format_inr(amount))
    accredited = col_b.checkbox("I hold a SEBI accredited investor certificate")

    for r in check_eligibility(data, amount, accredited):
        icon = "✅" if r["verdict"] == "open" else "❌"
        line = f"{icon} **{SHORT_NAMES.get(r['id'], r['name'])}**: {r['detail']} {badge(r['figure_status'])}"
        if r["caution"]:
            line += f" ⚠️ {r['caution']}"
        st.markdown(line)

    note = large_value_fund_note(data, amount, accredited)
    if note:
        st.info(note)

    st.caption("Meeting a minimum does not mean a product suits you, or that you meet its other "
               "conditions (KYC, residency, strategy risk). Check each offer document.")

# ---------- tab 3: sources ----------
with tab_sources:
    counts = {s: 0 for s in STATUS_ORDER}
    for v in vehicles.values():
        for f in v["facts"].values():
            counts[f["status"]] += 1
    st.write(" · ".join(f"{badge(s)} {STATUS_SHORT[s]}: {n}" for s, n in counts.items() if n))

    for vid, v in vehicles.items():
        with st.expander(SHORT_NAMES.get(vid, v["name"])):
            st.markdown(f"**Regulator:** {v['regulator']}  \n**Rulebook:** {v['regulation']}")
            for fact in v["facts"].values():
                st.markdown(f"**{fact['label']}** {badge(fact['status'])} _{STATUS_SHORT[fact['status']]}_")
                st.write(fact["value"])
                if fact.get("note"):
                    st.caption(fact["note"])
                if fact["sources"]:
                    for s in fact["sources"]:
                        st.markdown(f"- [{s['supports']}]({s['url']})")
                else:
                    st.caption("No source found.")

st.divider()
st.caption("Educational illustration only. Not investment advice. Rules and rates change; "
           "confirm with the regulator or a registered adviser before acting.")
