import streamlit as st

from src.dashboard.utils.db import get_latest_ratios

st.title("Stock Screener")

df = get_latest_ratios()  # one row per company

roe = st.sidebar.slider("ROE", 0, 50, 15)

de = st.sidebar.slider("D/E", 0.0, 5.0, 1.0)

out = df[

    (df["return_on_equity_pct"] >= roe)

    &

    (df["debt_to_equity"] <= de)

]

st.write(f"{len(out)} Companies")

st.dataframe(out)

st.download_button(

    "Download CSV",

    out.to_csv(index=False),

    "screener.csv",

    "text/csv"

)
