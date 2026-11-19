"""Relative valuation vs sector peers (FY-end snapshot from market_data).

    python -m src.analytics.valuation
"""

import sqlite3

import pandas as pd

from src.etl.config import DATABASE, OUTPUT


class Valuation:

    def __init__(self, db_path=DATABASE):

        self.conn = sqlite3.connect(db_path)

    def load(self):

        return pd.read_sql(
            """
            SELECT c.id AS company_id, c.company_name, c.broad_sector,
                   m.price_date, m.close_price, m.market_cap_cr, m.pe, m.pb, m.shares_source,
                   f.year, f.free_cash_flow_cr, f.return_on_equity_pct, f.composite_quality_score
            FROM companies c
            JOIN market_data m ON m.company_id = c.id
            LEFT JOIN financial_ratios f
                   ON f.company_id = c.id AND f.year = m.fiscal_year
            """,
            self.conn,
        )

    def run(self):

        df = self.load()

        df["fcf_yield_pct"] = (df["free_cash_flow_cr"] / df["market_cap_cr"] * 100).round(2)

        df["sector_pe"] = df.groupby("broad_sector")["pe"].transform("median").round(2)

        df["sector_peers"] = df.groupby("broad_sector")["pe"].transform("count")

        df["flag"] = "Fair"

        df.loc[df["pe"] > df["sector_pe"] * 1.5, "flag"] = "Caution"

        df.loc[df["pe"] < df["sector_pe"] * 0.7, "flag"] = "Discount"

        # a sector median of 1-2 companies is not meaningful; loss-makers have no P/E
        df.loc[(df["sector_peers"] < 3) | df["pe"].isna(), "flag"] = "Not Comparable"

        OUTPUT.mkdir(exist_ok=True)

        df.to_excel(OUTPUT / "valuation_summary.xlsx", index=False)

        df[df["flag"].isin(["Caution", "Discount"])].to_csv(OUTPUT / "valuation_flags.csv", index=False)

        print("Valuation complete.", df["flag"].value_counts().to_dict())

        return df


if __name__ == "__main__":
    Valuation().run()
