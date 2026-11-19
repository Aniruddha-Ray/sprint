import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import get_latest_ratios

st.title("Capital Allocation")

ratios = get_latest_ratios().dropna(subset=["capital_allocation_pattern"])

# Treemap areas can't be negative (FCF often is), so size by company count.
st.plotly_chart(

    px.treemap(

        ratios,

        path=["capital_allocation_pattern", "company_id"],

        color="free_cash_flow_cr",

        color_continuous_scale="RdYlGn",

    ),

    width="stretch"

)

pattern = st.selectbox(

    "Pattern",

    sorted(ratios["capital_allocation_pattern"].unique())

)

st.dataframe(ratios[ratios["capital_allocation_pattern"] == pattern])
