import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import get_ratios

st.title("Trend Analysis")

ratios = get_ratios()

ticker = st.selectbox("Company", sorted(ratios["company_id"].unique()))

metrics = st.multiselect(

    "Metrics",

    [
        "sales",
        "net_profit",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "revenue_cagr_5yr"
    ],

    default=["sales"]

)

df = ratios[ratios["company_id"] == ticker]

for metric in metrics:

    st.plotly_chart(px.line(df, x="year", y=metric, title=metric), width="stretch")
