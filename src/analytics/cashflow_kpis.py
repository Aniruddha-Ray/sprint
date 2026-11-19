"""Cash-flow KPIs.

Row-level helper functions (used by ratio_engine) plus the
CashFlowIntelligence report built on top of financial_ratios.

The raw data has no separate capex line, so cash from investing activity is
used as the capex proxy: FCF = CFO + CFI, capex = investing outflow.
"""

import math
import sqlite3

import pandas as pd

from src.etl.config import DATABASE, OUTPUT


def _missing(*values):
    for v in values:
        if v is None:
            return True
        try:
            if math.isnan(v):
                return True
        except TypeError:
            return True
    return False


# ---------------------------------------------------------
# Row-level KPI functions
# ---------------------------------------------------------

def free_cash_flow(operating_activity, investing_activity):
    if _missing(operating_activity, investing_activity):
        return None
    return round(operating_activity + investing_activity, 2)


def capex_amount(investing_activity):
    """Cash spent on investing (positive number), 0 if investing was a net inflow."""
    if _missing(investing_activity):
        return None
    return round(max(-investing_activity, 0.0), 2)


def cfo_quality_ratio(operating_activity, net_profit):
    """CFO / PAT. Undefined when PAT <= 0."""
    if _missing(operating_activity, net_profit) or net_profit <= 0:
        return None
    return round(operating_activity / net_profit, 2)


def cfo_quality_label(ratio):
    if ratio is None:
        return None
    if ratio > 1:
        return "High Quality"
    if ratio < 0.5:
        return "Accrual Risk"
    return "Moderate"


def capex_intensity(investing_activity, sales):
    """Investing outflow as % of sales."""
    capex = capex_amount(investing_activity)
    if capex is None or _missing(sales) or sales <= 0:
        return None
    return round(capex / sales * 100, 2)


def capex_label(intensity):
    if intensity is None:
        return None
    if intensity < 3:
        return "Asset Light"
    if intensity > 8:
        return "Capital Intensive"
    return "Moderate"


def fcf_conversion(fcf, operating_profit):
    """FCF as % of operating profit."""
    if _missing(fcf, operating_profit) or operating_profit <= 0:
        return None
    return round(fcf / operating_profit * 100, 2)


_PATTERNS = {
    # (CFO>=0, CFI>=0, CFF>=0)
    (True, False, False): "Self-Funded Growth & Shareholder Returns",
    (True, False, True): "Growth Funded by External Capital",
    (True, True, False): "Divesting & Deleveraging",
    (True, True, True): "Cash Accumulation",
    (False, False, True): "Distress - Financing Dependent",
    (False, True, True): "Distress - Asset Sales & Borrowing",
    (False, True, False): "Liquidating Assets",
    (False, False, False): "Cash Burn",
}


def capital_allocation_pattern(operating_activity, investing_activity, financing_activity, cfo_ratio=None):
    if _missing(operating_activity, investing_activity, financing_activity):
        return None
    key = (operating_activity >= 0, investing_activity >= 0, financing_activity >= 0)
    return _PATTERNS[key]


__all__ = [
    "free_cash_flow",
    "capex_amount",
    "cfo_quality_ratio",
    "cfo_quality_label",
    "capex_intensity",
    "capex_label",
    "fcf_conversion",
    "capital_allocation_pattern",
]


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

class CashFlowIntelligence:

    def __init__(self, db_path=DATABASE):

        self.conn = sqlite3.connect(db_path)

    def load(self):

        ratios = pd.read_sql("SELECT * FROM financial_ratios", self.conn)

        cash = pd.read_sql(
            "SELECT company_id, year, operating_activity, investing_activity, financing_activity FROM cashflow",
            self.conn,
        )

        profit = pd.read_sql("SELECT company_id, year, sales, net_profit FROM profitandloss", self.conn)

        companies = pd.read_sql("SELECT * FROM companies", self.conn)

        return ratios, cash, profit, companies

    def run(self):

        ratios, cash, profit, companies = self.load()

        df = (
            ratios
            .merge(cash, on=["company_id", "year"], how="left")
            .merge(profit, on=["company_id", "year"], how="left")
            .merge(companies, left_on="company_id", right_on="id", how="left")
        )

        latest = df.groupby("company_id")["year"].transform("max")

        latest_df = df[df["year"] == latest].copy()

        latest_df["cfo_quality_score"] = latest_df["cfo_quality_ratio"]

        latest_df["capex_intensity_pct"] = [
            capex_intensity(i, s) for i, s in zip(latest_df["investing_activity"], latest_df["sales"])
        ]

        latest_df["capex_label"] = latest_df["capex_intensity_pct"].map(
            lambda v: capex_label(None if pd.isna(v) else v)
        )

        latest_df["distress_flag"] = (
            (latest_df["cash_from_operations_cr"] < 0)
            & (latest_df["financing_activity"] > 0)
        )

        latest_df["deleveraging_flag"] = latest_df["financing_activity"] < 0

        latest_df = latest_df.rename(columns={"capital_allocation_pattern": "capital_allocation_label"})

        cols = [
            "company_id",
            "company_name",
            "broad_sector",  # not in the source data yet; kept if it is added
            "cfo_quality_score",
            "cfo_quality_label",
            "capex_intensity_pct",
            "capex_label",
            "free_cash_flow_cr",
            "fcf_conversion_pct",
            "distress_flag",
            "deleveraging_flag",
            "capital_allocation_label",
        ]

        OUTPUT.mkdir(exist_ok=True)

        latest_df[[c for c in cols if c in latest_df.columns]].to_excel(
            OUTPUT / "cashflow_intelligence.xlsx", index=False
        )

        latest_df[latest_df["distress_flag"]][
            ["company_id", "cash_from_operations_cr", "financing_activity", "net_profit"]
        ].to_csv(OUTPUT / "distress_alerts.csv", index=False)

        latest_df.groupby("capital_allocation_label").size().reset_index(name="count").to_csv(
            OUTPUT / "pattern_changes.csv", index=False
        )

        print("Cash Flow Intelligence Complete")


if __name__ == "__main__":
    CashFlowIntelligence().run()
