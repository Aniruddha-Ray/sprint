import sqlite3

import pandas as pd

import streamlit as st


DB = "db/nifty100.db"


@st.cache_data(ttl=600)
def query(sql):

    conn = sqlite3.connect(DB)

    df = pd.read_sql(sql, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_companies():

    return query(
        "SELECT * FROM companies"
    )


@st.cache_data(ttl=600)
def get_ratios():

    return query(
        "SELECT * FROM financial_ratios"
    )


@st.cache_data(ttl=600)
def get_sectors():

    return query(
        "SELECT * FROM sectors"
    )


@st.cache_data(ttl=600)
def get_peers():

    return query(
        "SELECT * FROM peer_percentiles"
    )


@st.cache_data(ttl=600)
def get_cashflow():

    return query(
        "SELECT * FROM cashflow"
    )


@st.cache_data(ttl=600)
def get_profit():

    return query(
        "SELECT * FROM profitandloss"
    )


@st.cache_data(ttl=600)
def get_balance():

    return query(
        "SELECT * FROM balancesheet"
    )