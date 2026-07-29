import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import *

st.title("Capital Allocation")

ratios = get_ratios()

fig = px.treemap(

    ratios,

    path=["capital_allocation_pattern","company_id"],

    values="free_cash_flow_cr"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

pattern = st.selectbox(

    "Pattern",

    sorted(

        ratios["capital_allocation_pattern"]

        .dropna()

        .unique()

    )

)

st.dataframe(

    ratios[

        ratios["capital_allocation_pattern"]==pattern

    ]

)