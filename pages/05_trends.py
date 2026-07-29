import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import *

st.title("Trend Analysis")

ratios = get_ratios()

ticker = st.selectbox(
    "Company",
    sorted(ratios["company_id"].unique())
)

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

df = ratios[
    ratios["company_id"] == ticker
]

for metric in metrics:

    if metric in df.columns:

        fig = px.line(
            df,
            x="year",
            y=metric,
            title=metric
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )