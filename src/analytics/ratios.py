"""
Financial Ratio Engine

Sprint 2
Day 08–09

Contains:
------------
Profitability Ratios
Leverage Ratios
Efficiency Ratios

All functions return either

float
or
None

No database code exists here.
"""

from typing import Optional


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

import math

def safe_divide(numerator, denominator):
    """
    Safely divide two numbers.

    Returns
    -------
    float | None
    """

    if numerator is None or denominator is None:
        return None

    try:
        if math.isnan(numerator) or math.isnan(denominator):
            return None
    except TypeError:
        pass

    if denominator == 0:
        return None

    return numerator / denominator


# ---------------------------------------------------------
# Profitability Ratios
# ---------------------------------------------------------

def net_profit_margin(
    net_profit: float,
    sales: float
) -> Optional[float]:
    """
    Net Profit Margin %

    Formula

    Net Profit / Sales ×100
    """

    value = safe_divide(net_profit, sales)

    if value is None:
        return None

    return round(value * 100, 2)


def operating_profit_margin(
    operating_profit: float,
    sales: float
) -> Optional[float]:

    """
    Operating Profit Margin %
    """

    value = safe_divide(
        operating_profit,
        sales
    )

    if value is None:
        return None

    return round(value * 100, 2)


def check_opm_difference(
    calculated_opm: Optional[float],
    source_opm: Optional[float],
    tolerance: float = 1.0
) -> bool:
    """
    Returns True if
    difference exceeds tolerance.

    Used for logging.
    """

    if calculated_opm is None:
        return False

    if source_opm is None:
        return False

    diff = abs(
        calculated_opm - source_opm
    )

    return diff > tolerance


def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    ROE %

    Net Profit

    -----------------

    Equity + Reserves
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(
        net_profit / equity * 100,
        2
    )


def return_on_capital_employed(
    operating_profit: float,
    interest: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> Optional[float]:
    """
    ROCE %

    EBIT

    ---------

    Capital Employed

    EBIT = Operating Profit + Interest
    """

    capital = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital <= 0:
        return None

    ebit = operating_profit + interest

    return round(
        ebit / capital * 100,
        2
    )


def return_on_assets(
    net_profit: float,
    total_assets: float
) -> Optional[float]:

    if total_assets <= 0:
        return None

    return round(
        net_profit /
        total_assets
        * 100,
        2
    )


# ---------------------------------------------------------
# Leverage Ratios
# ---------------------------------------------------------

def debt_to_equity(
    borrowings: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    Debt to Equity Ratio

    Formula:
        Borrowings / (Equity Capital + Reserves)

    Rules:
    - If borrowings == 0 → return 0
    - If denominator <= 0 → return None
    """

    if borrowings == 0:
        return 0.0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(
        borrowings / equity,
        2
    )


def high_leverage_flag(
    debt_to_equity_ratio: Optional[float],
    broad_sector: Optional[str]
) -> bool:
    """
    Returns True when

    D/E > 5

    except Financials sector.
    """

    if debt_to_equity_ratio is None:
        return False

    if broad_sector is not None:
        if broad_sector.lower() == "financials":
            return False

    return debt_to_equity_ratio > 5


def interest_coverage_ratio(
    operating_profit: float,
    other_income: float,
    interest: float
) -> Optional[float]:
    """
    Interest Coverage Ratio

    (Operating Profit + Other Income)

    --------------------------------

              Interest
    """

    if interest == 0:
        return None

    earnings = (
        operating_profit
        + other_income
    )

    return round(
        earnings / interest,
        2
    )


def icr_label(
    interest: float,
    icr: Optional[float]
) -> Optional[str]:
    """
    Display label.

    Sprint Requirement

    interest == 0

        →

    Debt Free
    """

    if interest == 0:
        return "Debt Free"

    if icr is None:
        return None

    return ""


def interest_risk_flag(
    icr: Optional[float]
) -> bool:
    """
    Company may not
    comfortably pay interest.

    Threshold = 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(
    borrowings: float,
    investments: float
) -> float:
    """
    Net Debt

    Borrowings - Investments
    """

    return round(
        borrowings - investments,
        2
    )

# ---------------------------------------------------------
# Efficiency Ratios
# ---------------------------------------------------------

def asset_turnover(
    sales: float,
    total_assets: float
) -> Optional[float]:
    """
    Asset Turnover Ratio

    Sales
    -----
    Total Assets
    """

    if total_assets <= 0:
        return None

    return round(
        sales / total_assets,
        2
    )


def earnings_per_share(
    net_profit: float,
    equity_capital: float,
    face_value: float = 10
) -> Optional[float]:
    """
    EPS

    Number of shares is approximated as

    equity_capital / face_value
    """

    if equity_capital <= 0:
        return None

    if face_value <= 0:
        return None

    shares = equity_capital / face_value

    if shares <= 0:
        return None

    return round(
        net_profit / shares,
        2
    )


def book_value_per_share(
    equity_capital: float,
    reserves: float,
    face_value: float = 10
) -> Optional[float]:
    """
    Book Value Per Share
    """

    if equity_capital <= 0:
        return None

    shares = equity_capital / face_value

    if shares <= 0:
        return None

    return round(
        (equity_capital + reserves) / shares,
        2
    )


def dividend_payout_ratio(
    dividend_payout: float,
    net_profit: float
) -> Optional[float]:
    """
    Dividend Payout %

    Dividend Paid
    -------------
    Net Profit
    """

    if net_profit == 0:
        return None

    return round(
        dividend_payout / net_profit * 100,
        2
    )


# ---------------------------------------------------------
# Quality Score
# ---------------------------------------------------------

def profitability_score(
    roe: Optional[float],
    roce: Optional[float],
    npm: Optional[float]
) -> int:
    """
    Maximum score = 3
    """

    score = 0

    if roe is not None and roe >= 15:
        score += 1

    if roce is not None and roce >= 15:
        score += 1

    if npm is not None and npm >= 10:
        score += 1

    return score


def leverage_score(
    debt_equity: Optional[float],
    icr: Optional[float]
) -> int:
    """
    Maximum score = 2
    """

    score = 0

    if debt_equity is not None and debt_equity < 1:
        score += 1

    if icr is not None and icr >= 3:
        score += 1

    return score


def efficiency_score(
    asset_turnover_ratio: Optional[float]
) -> int:
    """
    Maximum score = 1
    """

    if asset_turnover_ratio is None:
        return 0

    if asset_turnover_ratio >= 1:
        return 1

    return 0


def composite_quality_score(
    roe: Optional[float],
    roce: Optional[float],
    npm: Optional[float],
    debt_equity: Optional[float],
    icr: Optional[float],
    asset_turnover_ratio: Optional[float]
) -> int:
    """
    Overall Quality Score

    Maximum = 6
    """

    score = 0

    score += profitability_score(
        roe,
        roce,
        npm
    )

    score += leverage_score(
        debt_equity,
        icr
    )

    score += efficiency_score(
        asset_turnover_ratio
    )

    return score

# ---------------------------------------------------------
# Module Exports
# ---------------------------------------------------------

__all__ = [
    "safe_divide",

    # Profitability
    "net_profit_margin",
    "operating_profit_margin",
    "check_opm_difference",
    "return_on_equity",
    "return_on_capital_employed",
    "return_on_assets",

    # Leverage
    "debt_to_equity",
    "high_leverage_flag",
    "interest_coverage_ratio",
    "icr_label",
    "interest_risk_flag",
    "net_debt",

    # Efficiency
    "asset_turnover",
    "earnings_per_share",
    "book_value_per_share",
    "dividend_payout_ratio",

    # Quality
    "profitability_score",
    "leverage_score",
    "efficiency_score",
    "composite_quality_score"
]


# ---------------------------------------------------------
# Self Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("Financial Ratio Engine")
    print("=" * 60)

    npm = net_profit_margin(500, 5000)
    print("Net Profit Margin:", npm)

    opm = operating_profit_margin(900, 5000)
    print("Operating Profit Margin:", opm)

    print(
        "OPM Difference >1%:",
        check_opm_difference(
            opm,
            17.8
        )
    )

    roe = return_on_equity(
        1200,
        800,
        4200
    )

    print("ROE:", roe)

    roce = return_on_capital_employed(
        operating_profit=1800,
        interest=120,
        equity_capital=800,
        reserves=4200,
        borrowings=1500
    )

    print("ROCE:", roce)

    roa = return_on_assets(
        1200,
        9500
    )

    print("ROA:", roa)

    de = debt_to_equity(
        1500,
        800,
        4200
    )

    print("Debt / Equity:", de)

    icr = interest_coverage_ratio(
        1800,
        100,
        150
    )

    print("Interest Coverage:", icr)

    print(
        "High Leverage:",
        high_leverage_flag(
            de,
            "IT"
        )
    )

    print(
        "Interest Risk:",
        interest_risk_flag(icr)
    )

    print(
        "Net Debt:",
        net_debt(
            1500,
            300
        )
    )

    turnover = asset_turnover(
        5000,
        9500
    )

    print(
        "Asset Turnover:",
        turnover
    )

    eps = earnings_per_share(
        1200,
        800,
        10
    )

    print("EPS:", eps)

    bvps = book_value_per_share(
        800,
        4200,
        10
    )

    print("Book Value/Share:", bvps)

    payout = dividend_payout_ratio(
        200,
        1200
    )

    print("Dividend Payout:", payout)

    score = composite_quality_score(
        roe=roe,
        roce=roce,
        npm=npm,
        debt_equity=de,
        icr=icr,
        asset_turnover_ratio=turnover
    )

    print("Composite Quality Score:", score)

    print("=" * 60)
    print("All ratio functions executed successfully.")
    print("=" * 60)

