import sqlite3

import pytest

from src.etl.config import DATABASE


@pytest.fixture(scope="module")
def conn():
    if not DATABASE.exists():
        pytest.skip("database not built - run `make run`")
    c = sqlite3.connect(DATABASE)
    yield c
    c.close()


def test_financial_ratios_populated(conn):
    rows = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    companies = conn.execute("SELECT COUNT(DISTINCT company_id) FROM financial_ratios").fetchone()[0]
    assert rows > 0
    assert companies == conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]


def test_one_row_per_company_year(conn):
    dupes = conn.execute(
        "SELECT COUNT(*) FROM (SELECT company_id, year FROM financial_ratios GROUP BY 1, 2 HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    assert dupes == 0


def test_no_foreign_key_violations(conn):
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_quality_score_in_range(conn):
    lo, hi = conn.execute(
        "SELECT MIN(composite_quality_score), MAX(composite_quality_score) FROM financial_ratios"
    ).fetchone()
    assert 0 <= lo <= hi <= 6


def test_market_data_complete(conn):
    total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    with_sector = conn.execute("SELECT COUNT(*) FROM companies WHERE broad_sector IS NOT NULL").fetchone()[0]
    with_mcap = conn.execute("SELECT COUNT(*) FROM market_data WHERE market_cap_cr > 0").fetchone()[0]
    assert with_sector == total
    assert with_mcap == total


def test_abb_row_is_abbott_india(conn):
    # id 'ABB' in the source is Abbott India; prices must come from ABBOTINDIA
    assert conn.execute("SELECT nse_symbol FROM companies WHERE id = 'ABB'").fetchone()[0] == "ABBOTINDIA"


def test_corrupt_balance_sheets_produce_no_roe(conn):
    # balancesheet.xlsx has total assets ~1-5% of sales for these in every year
    computed = conn.execute(
        "SELECT COUNT(*) FROM financial_ratios "
        "WHERE company_id IN ('BEL', 'HAL', 'INDIGO', 'LT') AND return_on_equity_pct IS NOT NULL"
    ).fetchone()[0]
    assert computed == 0
