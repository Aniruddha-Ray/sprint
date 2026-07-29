import sqlite3
import pandas as pd


class Valuation:

    def __init__(self):

        self.conn = sqlite3.connect(
            "db/nifty100.db"
        )

    def run(self):

        ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        companies = pd.read_sql(

            "SELECT * FROM companies",

            self.conn

        )

        df = ratios.merge(

            companies,

            left_on="company_id",

            right_on="id",

            how="left"

        )

        df["fcf_yield_pct"] = (

            df["free_cash_flow_cr"]

            /

            df["market_cap"]

        ) * 100

        median = (

            df.groupby("broad_sector")["pe"]

            .transform("median")

        )

        df["sector_pe"] = median

        df["flag"] = "Fair"

        df.loc[

            df["pe"] > df["sector_pe"] * 1.5,

            "flag"

        ] = "Caution"

        df.loc[

            df["pe"] < df["sector_pe"] * 0.7,

            "flag"

        ] = "Discount"

        df.to_excel(

            "output/valuation_summary.xlsx",

            index=False

        )

        df[

            df["flag"]!="Fair"

        ].to_csv(

            "output/valuation_flags.csv",

            index=False

        )

        print("Valuation complete.")


if __name__=="__main__":

    Valuation().run()