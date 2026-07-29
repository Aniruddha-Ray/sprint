from typing import Optional, Tuple
import math
import pandas as pd

# Status Flags
NORMAL = "NORMAL"
ZERO_BASE = "ZERO_BASE"
TURNAROUND = "TURNAROUND"
DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
BOTH_NEGATIVE = "BOTH_NEGATIVE"
INSUFFICIENT = "INSUFFICIENT"

def valid_number(value):

    if value is None:
        return False

    if pd.isna(value):
        return False

    return True
    
def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int
) -> Tuple[Optional[float], str]:
    """
    Generic CAGR Calculator

    Returns
    -------
    (value, flag)
    """

    # Less than required years

    if years <= 0:
        return None, INSUFFICIENT

    # Invalid numbers

    if (
        not valid_number(start_value)
        or
        not valid_number(end_value)
    ):
        return None, INSUFFICIENT

    # Zero Base

    if start_value == 0:
        return None, ZERO_BASE

    # Positive -> Negative

    if start_value > 0 and end_value < 0:
        return None, DECLINE_TO_LOSS

    # Negative -> Positive

    if start_value < 0 and end_value > 0:
        return None, TURNAROUND

    # Negative -> Negative

    if start_value < 0 and end_value < 0:
        return None, BOTH_NEGATIVE

    value = (
        (
            end_value / start_value
        ) ** (1 / years)
        - 1
    ) * 100

    return round(value, 2), NORMAL

def revenue_cagr(
    start_sales,
    end_sales,
    years
):
    return calculate_cagr(
        start_sales,
        end_sales,
        years
    )


def pat_cagr(
    start_profit,
    end_profit,
    years
):
    return calculate_cagr(
        start_profit,
        end_profit,
        years
    )


def eps_cagr(
    start_eps,
    end_eps,
    years
):
    return calculate_cagr(
        start_eps,
        end_eps,
        years
    )

__all__ = [

    "calculate_cagr",

    "revenue_cagr",

    "pat_cagr",

    "eps_cagr",

    "NORMAL",

    "ZERO_BASE",

    "TURNAROUND",

    "DECLINE_TO_LOSS",

    "BOTH_NEGATIVE",

    "INSUFFICIENT"

]

if __name__ == "__main__":

    tests = [

        (100, 200, 5),

        (100, -50, 5),

        (-100, 200, 5),

        (-100, -50, 5),

        (0, 100, 5),

        (100, 150, 0)

    ]

    for s, e, y in tests:

        value, flag = calculate_cagr(
            s,
            e,
            y
        )

        print(
            s,
            e,
            y,
            value,
            flag
        )

