import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import get_companies, get_ratios

st.title("Company Profile")

companies = get_companies()

ticker = st.selectbox(

    "Company",

    companies["id"],

    format_func=lambda t: f"{t} - {companies.set_index('id').at[t, 'company_name']}",

)

ratio = get_ratios()

df = ratio[ratio["company_id"] == ticker]

if len(df) == 0:

    st.warning("No financial data for this ticker.")

    st.stop()

latest = df.sort_values("year").iloc[-1]

c1, c2, c3 = st.columns(3)

c1.metric("ROE", latest["return_on_equity_pct"])

c2.metric("ROCE", latest["return_on_capital_employed_pct"])

c3.metric("D/E", latest["debt_to_equity"])

st.plotly_chart(px.line(df, x="year", y="sales", title="Revenue"), width="stretch")

st.plotly_chart(px.line(df, x="year", y="net_profit", title="Net Profit"), width="stretch")
