import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import *

st.title("🏠 Home")

companies = get_companies()

ratios = get_ratios()

sectors = get_sectors()

col1,col2,col3,col4,col5,col6 = st.columns(6)

col1.metric(
    "Companies",
    len(companies)
)

col2.metric(
    "Average ROE",
    round(ratios["return_on_equity_pct"].mean(),2)
)

col3.metric(
    "Median D/E",
    round(ratios["debt_to_equity"].median(),2)
)

col4.metric(
    "Median CAGR",
    round(ratios["revenue_cagr_5yr"].median(),2)
)

col5.metric(
    "Debt Free",
    (ratios["debt_to_equity"]==0).sum()
)

col6.metric(
    "Rows",
    len(ratios)
)

fig = px.pie(

    sectors,

    names="broad_sector"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Top Quality")

st.dataframe(

    ratios.sort_values(

        "composite_quality_score",

        ascending=False

    ).head(10)

)