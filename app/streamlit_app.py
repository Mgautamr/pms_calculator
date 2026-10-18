import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import streamlit.components.v1 as components

from app import theme

st.set_page_config(page_title="Hurdle: a PMS toolkit", page_icon="₹", layout="wide")
theme.apply()

PAGES = {
    "Fee_Calculator": "pages/1_Fee_Calculator.py",
    "Compare_Vehicles": "pages/2_Compare_Vehicles.py",
    "Portfolio_Dashboard": "pages/3_Portfolio_Dashboard.py",
}

# The landing page is a two-way component: clicking a tool sends its name back here.
landing = components.declare_component("hurdle_landing", path=str(Path(__file__).parent / "landing_component"))
choice = landing(key="landing", default=None)
if isinstance(choice, dict) and choice.get("tool") in PAGES:
    st.switch_page(PAGES[choice["tool"]])

theme.footnote("Educational illustration only, not investment advice. All returns and fees are "
               "assumptions you enter or sample data, not real fund data.")
