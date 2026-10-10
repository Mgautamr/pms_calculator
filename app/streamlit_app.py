import streamlit as st

st.set_page_config(page_title="PMS Toolkit", page_icon="₹", layout="wide")

st.title("PMS Toolkit")
st.write(
    "Tools to understand Portfolio Management Services (PMS) in India: "
    "see how different fee structures change what an investor actually keeps."
)
st.markdown(
    "- **Fee Calculator** (in the sidebar): compare fixed, hybrid, hurdle and "
    "high-water-mark fee structures on the same returns."
)
st.caption(
    "Educational illustration only. Not investment advice. "
    "All returns and fees are assumptions you enter, not real fund data."
)
