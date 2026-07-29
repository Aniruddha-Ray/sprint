import sqlite3
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class CompanyClustering:

    def __init__(self):

        self.conn = sqlite3.connect(
            "db/nifty100.db"
        )

    def load(self):

        ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        companies = pd.read_sql(

            "SELECT * FROM companies",

            self.conn

        )

        latest = ratios.groupby(

            "company_id"

        )["year"].transform("max")

        ratios = ratios[
            ratios["year"] == latest
        ]

        df = companies.merge(

            ratios,

            left_on="id",

            right_on="company_id",

            how="left"

        )

        return df

    def run(self):

        df = self.load()

        features = [

            "return_on_equity_pct",

            "return_on_capital_employed_pct",

            "net_profit_margin_pct",

            "debt_to_equity",

            "revenue_cagr_5yr",

            "pat_cagr_5yr",

            "asset_turnover",

            "free_cash_flow_cr"

        ]

        X = df[features].fillna(0)

        scaler = StandardScaler()

        X = scaler.fit_transform(X)

        model = KMeans(

            n_clusters=5,

            random_state=42,

            n_init="auto"

        )

        df["cluster"] = model.fit_predict(X)

        df.to_csv(

            "output/company_clusters.csv",

            index=False

        )

        df[

            ["company_id", "cluster"]

        ].to_sql(

            "company_clusters",

            self.conn,

            if_exists="replace",

            index=False

        )

        print("Clusters Generated")


if __name__ == "__main__":

    CompanyClustering().run()