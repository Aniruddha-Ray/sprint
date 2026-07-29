import streamlit as st

from src.dashboard.utils.db import *

st.title("Annual Reports")

companies = get_companies()

ticker = st.selectbox(

    "Company",

    companies["company_id"]

)

docs = query(

    f"""

    SELECT *

    FROM documents

    WHERE company_id='{ticker}'

    """

)

if len(docs)==0:

    st.warning("No reports found.")

else:

    st.dataframe(docs)