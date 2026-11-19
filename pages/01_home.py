import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import get_companies, get_latest_ratios, get_sectors

st.title("🏠 Home")

companies = get_companies()

ratios = get_latest_ratios()  # latest year per company

sectors = get_sectors()

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Companies", len(companies))

col2.metric("Average ROE", round(ratios["return_on_equity_pct"].mean(), 2))

col3.metric("Median D/E", round(ratios["debt_to_equity"].median(), 2))

col4.metric("Median 5Y Rev CAGR", round(ratios["revenue_cagr_5yr"].median(), 2))

col5.metric("Debt Free", int((ratios["debt_to_equity"] == 0).sum()))

col6.metric("Latest Year Rows", len(ratios))

if companies.get("broad_sector") is not None and companies["broad_sector"].notna().any():
    st.plotly_chart(px.pie(companies, names="broad_sector"), width="stretch")
elif not sectors.empty:
    st.plotly_chart(px.pie(sectors, names="sector_name"), width="stretch")
else:
    st.info("No sector data available yet (companies sheet has no sector column).")

st.subheader("Top Quality")

st.dataframe(

    ratios.sort_values(

        "composite_quality_score",

        ascending=False

    ).head(10)

)
