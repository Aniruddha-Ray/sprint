import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import *

st.title("Sector Analysis")

companies = get_companies()

ratios = get_ratios()

df = companies.merge(
    ratios,
    left_on="id",
    right_on="company_id",
    how="left"
)

sector = st.selectbox(
    "Sector",
    sorted(df["broad_sector"].dropna().unique())
)

temp = df[
    df["broad_sector"] == sector
]

fig = px.scatter(

    temp,

    x="sales",

    y="return_on_equity_pct",

    size="market_cap",

    color="sub_sector",

    hover_name="company_id"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Sector Data")

st.dataframe(temp)