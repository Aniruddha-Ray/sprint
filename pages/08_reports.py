import streamlit as st

from src.dashboard.utils.db import get_companies, query

st.title("Annual Reports")

companies = get_companies()

ticker = st.selectbox("Company", companies["id"])

docs = query(

    "SELECT year, annual_report FROM documents WHERE company_id = ? ORDER BY year DESC",

    (ticker,)

)

if len(docs) == 0:

    st.warning("No reports found.")

else:

    st.dataframe(

        docs,

        column_config={"annual_report": st.column_config.LinkColumn("Annual Report")}

    )
