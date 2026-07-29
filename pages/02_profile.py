import streamlit as st

import plotly.express as px

from src.dashboard.utils.db import *

st.title("Company Profile")

companies = get_companies()

ticker = st.selectbox(

    "Company",

    companies["company_id"]

)

ratio = get_ratios()

df = ratio[
    ratio["company_id"]==ticker
]

if len(df)==0:

    st.warning("Ticker not found.")

    st.stop()

latest = df.sort_values(
    "year"
).iloc[-1]

c1,c2,c3 = st.columns(3)

c1.metric(
    "ROE",
    latest["return_on_equity_pct"]
)

c2.metric(
    "ROCE",
    latest["return_on_capital_employed_pct"]
)

c3.metric(
    "D/E",
    latest["debt_to_equity"]
)

fig = px.line(

    df,

    x="year",

    y="sales",

    title="Revenue"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

fig = px.line(

    df,

    x="year",

    y="net_profit",

    title="Net Profit"

)

st.plotly_chart(
    fig,
    use_container_width=True
)