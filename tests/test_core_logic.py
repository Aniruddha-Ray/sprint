"""Regression tests for bugs fixed during the codebase debug pass."""

import pandas as pd
import pytest

from src.analytics.cagr import INSUFFICIENT, NORMAL
from src.analytics.cashflow_kpis import capital_allocation_pattern, free_cash_flow
from src.analytics.ratio_engine import CAGRCalculator
from src.analytics.ratios import return_on_capital_employed
from src.etl.normaliser import normalize_year
from src.etl.validator import DataValidator


@pytest.mark.parametrize("raw, expected", [
    ("Mar 2013", 2013),
    ("Dec 2012", 2012),
    ("Mar 2024 9m", 2024),
    ("Mar-13", 2013),      # two-digit form used in cashflow.xlsx
    ("2013.0", 2013),      # float-ish form used in balancesheet.xlsx
    (2013, 2013),
    ("TTM", None),
    (None, None),
    (float("nan"), None),
])
def test_normalize_year(raw, expected):
    assert normalize_year(raw) == expected


def test_roce_uses_pbt_plus_interest():
    # EBIT = 1500 + 120 = 1620 ; capital employed = 800 + 4200 + 1500 = 6500
    assert return_on_capital_employed(1500, 120, 800, 4200, 1500) == round(1620 / 6500 * 100, 2)


def test_cagr_processes_every_company_and_respects_year_gaps():
    df = pd.DataFrame({
        "company_id": ["A"] * 4 + ["B"] * 4,
        # B has a gap: 2016 is missing, so 2017's 3y window must use 2014
        "year": [2014, 2015, 2016, 2017, 2013, 2014, 2015, 2017],
        "sales": [100, 110, 120, 133.1, 50, 100, 120, 200],
        "net_profit": [10] * 8,
        "eps": [1] * 8,
    })

    out = CAGRCalculator.compute(df).set_index(["company_id", "year"])

    assert set(out.index.get_level_values(0)) == {"A", "B"}  # used to return after the first company
    assert out.loc[("A", 2017), "revenue_cagr_3yr"] == 10.0
    assert out.loc[("B", 2017), "revenue_cagr_3yr"] == 25.99  # (200/100)^(1/3)-1, 2014 -> 2017
    assert out.loc[("B", 2017), "revenue_cagr_3yr_flag"] == NORMAL
    assert out.loc[("A", 2016), "revenue_cagr_3yr_flag"] == INSUFFICIENT


def test_validator_fk_checks_company_id_not_row_id():
    v = DataValidator()
    parent = pd.DataFrame({"id": ["TCS", "INFY"]})
    child = pd.DataFrame({"id": [1, 2, 3], "company_id": ["TCS", "INFY", "NOPE"]})

    v.check_foreign_key(child, parent)

    assert [f["message"] for f in v.failures] == ["Invalid FK NOPE"]


def test_validator_balance_sheet_liabilities_include_equity():
    v = DataValidator()
    ok = pd.DataFrame({"total_assets": [907], "total_liabilities": [907], "equity_capital": [21]})

    v.check_balance_sheet(ok)

    assert v.failures == []


def test_cashflow_kpis():
    assert free_cash_flow(1213, -416) == 797
    assert free_cash_flow(None, -416) is None
    assert capital_allocation_pattern(100, -50, -30) == "Self-Funded Growth & Shareholder Returns"
    assert capital_allocation_pattern(-10, -5, 20) == "Distress - Financing Dependent"
