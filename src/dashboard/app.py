import streamlit as st

st.set_page_config(

    page_title="Nifty 100 Analytics",

    layout="wide",

    initial_sidebar_state="expanded"

)

st.title("📈 Nifty 100 Analytics Dashboard")

st.sidebar.success("Select a page from sidebar.")

st.write(
"""
Welcome to the Financial Analytics Dashboard.

Use the Pages section on the left.
"""
)