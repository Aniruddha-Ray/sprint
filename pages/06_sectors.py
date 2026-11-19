import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import get_companies, get_latest_ratios

st.title("Sector Analysis")

companies = get_companies()

if "broad_sector" not in companies.columns or companies["broad_sector"].isna().all():

    st.info(
        "Sector analysis needs sector data. Run `python -m src.etl.market_data` "
        "then `python -m src.etl.load_database`."
    )

    st.stop()

df = companies.merge(get_latest_ratios(), left_on="id", right_on="company_id", how="left")

sector = st.selectbox("Sector", sorted(df["broad_sector"].dropna().unique()))

temp = df[df["broad_sector"] == sector]

st.plotly_chart(

    px.scatter(

        temp,

        x="sales",

        y="return_on_equity_pct",

        size=temp["market_cap_cr"].fillna(0) if "market_cap_cr" in temp.columns else None,

        color="sub_sector" if "sub_sector" in temp.columns else None,

        hover_name="company_id"

    ),

    width="stretch"

)

st.subheader("Sector Data")

st.dataframe(temp)
