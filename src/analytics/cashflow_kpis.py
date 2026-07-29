import sqlite3
import pandas as pd


class CashFlowIntelligence:

    def __init__(self):

        self.conn = sqlite3.connect(
            "db/nifty100.db"
        )

    def load(self):

        ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        cash = pd.read_sql(

            "SELECT * FROM cashflow",

            self.conn

        )

        companies = pd.read_sql(

            "SELECT * FROM companies",

            self.conn

        )

        return ratios, cash, companies

    def run(self):

        ratios, cash, companies = self.load()

        df = ratios.merge(

            cash,

            on=["company_id", "year"],

            how="left"

        )

        df = df.merge(

            companies,

            left_on="company_id",

            right_on="id",

            how="left"

        )

        latest = df.groupby(

            "company_id"

        )["year"].transform("max")

        latest_df = df[df["year"] == latest].copy()

        latest_df["cfo_quality_score"] = (

            latest_df["cash_from_operations_cr"]

            /

            latest_df["net_profit"]

        )

        latest_df["cfo_quality_label"] = "Moderate"

        latest_df.loc[
            latest_df["cfo_quality_score"] > 1,
            "cfo_quality_label"
        ] = "High Quality"

        latest_df.loc[
            latest_df["cfo_quality_score"] < 0.5,
            "cfo_quality_label"
        ] = "Accrual Risk"

        latest_df["capex_intensity_pct"] = (

            latest_df["capex_cr"].abs()

            /

            latest_df["sales"]

        ) * 100

        latest_df["capex_label"] = "Moderate"

        latest_df.loc[
            latest_df["capex_intensity_pct"] < 3,
            "capex_label"
        ] = "Asset Light"

        latest_df.loc[
            latest_df["capex_intensity_pct"] > 8,
            "capex_label"
        ] = "Capital Intensive"

        latest_df["distress_flag"] = (

            (latest_df["cash_from_operations_cr"] < 0)

            &

            (latest_df["financing_activity"] > 0)

        )

        latest_df["deleveraging_flag"] = (

            latest_df["financing_activity"] < 0

        )

        if "capital_allocation_pattern" not in latest_df.columns:

            latest_df["capital_allocation_pattern"] = "Mixed"

        latest_df.rename(

            columns={

                "capital_allocation_pattern":

                "capital_allocation_label"

            },

            inplace=True

        )

        cols = [

            "company_id",

            "company_name",

            "broad_sector",

            "cfo_quality_score",

            "cfo_quality_label",

            "capex_intensity_pct",

            "capex_label",

            "free_cash_flow_cr",

            "fcf_conversion_pct",

            "distress_flag",

            "deleveraging_flag",

            "capital_allocation_label"

        ]

        output = latest_df[cols]

        output.to_excel(

            "output/cashflow_intelligence.xlsx",

            index=False

        )

        latest_df[

            latest_df["distress_flag"]

        ][

            [

                "company_id",

                "cash_from_operations_cr",

                "financing_activity",

                "net_profit"

            ]

        ].to_csv(

            "output/distress_alerts.csv",

            index=False

        )

        latest_df.groupby(

            "capital_allocation_label"

        ).size().reset_index(

            name="count"

        ).to_csv(

            "output/pattern_changes.csv",

            index=False

        )

        print("Cash Flow Intelligence Complete")


if __name__ == "__main__":

    CashFlowIntelligence().run()