import sqlite3

import pandas as pd
import streamlit as st

from src.etl.config import DATABASE

DB = str(DATABASE)


@st.cache_data(ttl=600)
def query(sql, params=()):

    conn = sqlite3.connect(DB)

    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()


@st.cache_data(ttl=600)
def table_exists(name):

    return len(query("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))) > 0


def _table_or_empty(name):

    return query(f"SELECT * FROM {name}") if table_exists(name) else pd.DataFrame()


@st.cache_data(ttl=600)
def get_companies():

    if not table_exists("market_data"):
        return query("SELECT * FROM companies")

    return query(
        """
        SELECT c.*, m.close_price, m.market_cap_cr, m.pe, m.pb, m.price_date
        FROM companies c LEFT JOIN market_data m ON m.company_id = c.id
        """
    )


@st.cache_data(ttl=600)
def get_ratios():
    """All company-years, joined with P&L so sales / net_profit are available."""

    return query(
        """
        SELECT f.*, p.sales, p.net_profit, p.operating_profit
        FROM financial_ratios f
        LEFT JOIN profitandloss p USING (company_id, year)
        ORDER BY f.company_id, f.year
        """
    )


@st.cache_data(ttl=600)
def get_latest_ratios():
    """One row per company: its most recent year."""

    df = get_ratios()

    return df[df["year"] == df.groupby("company_id")["year"].transform("max")]


@st.cache_data(ttl=600)
def get_sectors():

    return _table_or_empty("sectors")


@st.cache_data(ttl=600)
def get_peers():

    return _table_or_empty("peer_percentiles")


@st.cache_data(ttl=600)
def get_cashflow():

    return query("SELECT * FROM cashflow")


@st.cache_data(ttl=600)
def get_profit():

    return query("SELECT * FROM profitandloss")


@st.cache_data(ttl=600)
def get_balance():

    return query("SELECT * FROM balancesheet")
