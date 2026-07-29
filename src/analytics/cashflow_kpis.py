from typing import Optional
import pandas as pd

def free_cash_flow(
    operating_activity: float,
    investing_activity: float
) -> float:
    """
    FCF = CFO + CFI

    Investing activity is normally negative,
    so this effectively becomes

    CFO - CapEx
    """

    return round(
        operating_activity + investing_activity,
        2
    )

def cfo_quality_ratio(
    operating_activity: float,
    net_profit: float
) -> Optional[float]:

    if net_profit == 0:
        return None

    return round(
        operating_activity / net_profit,
        2
    )


def cfo_quality_label(
    ratio: Optional[float]
) -> Optional[str]:

    if ratio is None:
        return None

    if ratio > 1:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"

def capex_intensity(
    investing_activity: float,
    sales: float
) -> Optional[float]:

    if sales == 0:
        return None

    return round(
        abs(investing_activity) / sales * 100,
        2
    )


def capex_label(
    intensity: Optional[float]
):

    if intensity is None:
        return None

    if intensity < 3:
        return "Asset Light"

    if intensity <= 8:
        return "Moderate"

    return "Capital Intensive"

def fcf_conversion(
    free_cash_flow_value: float,
    operating_profit: float
):

    if operating_profit == 0:
        return None

    return round(
        free_cash_flow_value /
        operating_profit *
        100,
        2
    )

def sign(value):

    if value is None:
        return "0"

    try:
        if value > 0:
            return "+"

        if value < 0:
            return "-"

    except TypeError:
        return "0"

    return "0"


def capital_allocation_pattern(
    cfo,
    cfi,
    cff,
    cfo_pat_ratio=None
):

    s = (
        sign(cfo),
        sign(cfi),
        sign(cff)
    )

    if s == ("+","-","-"):

        if (
            cfo_pat_ratio is not None
            and
            cfo_pat_ratio > 1
        ):
            return "Shareholder Returns"

        return "Reinvestor"

    if s == ("+","+","-"):
        return "Liquidating Assets"

    if s == ("-","+","+"):
        return "Distress Signal"

    if s == ("-","-","+"):
        return "Growth Funded by Debt"

    if s == ("+","+","+"):
        return "Cash Accumulator"

    if s == ("-","-","-"):
        return "Pre-Revenue"

    if s == ("+","-","+"):
        return "Mixed"

    return "Other"

def generate_capital_allocation_csv(
    df,
    output_path="output/capital_allocation.csv"
):

    records = []

    for _, row in df.iterrows():

        ratio = cfo_quality_ratio(
            row["operating_activity"],
            row["net_profit"]
        )

        pattern = capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"],
            ratio
        )

        records.append({

            "company_id":
                row["company_id"],

            "year":
                row["year"],

            "cfo_sign":
                sign(row["operating_activity"]),

            "cfi_sign":
                sign(row["investing_activity"]),

            "cff_sign":
                sign(row["financing_activity"]),

            "pattern_label":
                pattern

        })

    out = pd.DataFrame(records)

    out.to_csv(
        output_path,
        index=False
    )

    return out

__all__ = [

    "free_cash_flow",

    "cfo_quality_ratio",

    "cfo_quality_label",

    "capex_intensity",

    "capex_label",

    "fcf_conversion",

    "capital_allocation_pattern",

    "generate_capital_allocation_csv"
]

if __name__ == "__main__":

    fcf = free_cash_flow(
        1200,
        -350
    )

    print("FCF:", fcf)

    ratio = cfo_quality_ratio(
        1200,
        900
    )

    print("CFO/PAT:", ratio)

    print(
        cfo_quality_label(ratio)
    )

    intensity = capex_intensity(
        -350,
        5000
    )

    print(
        "CapEx Intensity:",
        intensity
    )

    print(
        capex_label(intensity)
    )

    print(
        "FCF Conversion:",
        fcf_conversion(
            fcf,
            1500
        )
    )

    print(
        capital_allocation_pattern(
            1200,
            -350,
            -250,
            ratio
        )
    )

