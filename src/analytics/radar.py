import os
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class RadarChartGenerator:

    def __init__(self, db_path="db/nifty100.db"):

        self.conn = sqlite3.connect(db_path)

        os.makedirs(
            "reports/radar_charts",
            exist_ok=True
        )

    def load(self):

        ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        peers = pd.read_sql(
            "SELECT * FROM peer_groups",
            self.conn
        )

        return ratios.merge(
            peers,
            on="company_id",
            how="left"
        )

    def generate(self):

        df = self.load()

        metrics = [

            "return_on_equity_pct",

            "return_on_capital_employed_pct",

            "net_profit_margin_pct",

            "debt_to_equity",

            "free_cash_flow_cr",

            "pat_cagr_5yr",

            "revenue_cagr_5yr",

            "composite_quality_score"

        ]

        labels = [

            "ROE",

            "ROCE",

            "NPM",

            "D/E",

            "FCF",

            "PAT CAGR",

            "REV CAGR",

            "Score"

        ]

        for _, row in df.iterrows():

            values = []

            for col in metrics:

                value = row.get(col, 0)

                if pd.isna(value):
                    value = 0

                values.append(value)

            values.append(values[0])

            angles = np.linspace(
                0,
                2 * np.pi,
                len(labels),
                endpoint=False
            ).tolist()

            angles.append(angles[0])

            fig = plt.figure(figsize=(6, 6))

            ax = plt.subplot(
                111,
                polar=True
            )

            ax.plot(
                angles,
                values,
                linewidth=2
            )

            ax.fill(
                angles,
                values,
                alpha=0.25
            )

            ax.set_xticks(
                angles[:-1]
            )

            ax.set_xticklabels(
                labels
            )

            title = f"{row['company_id']}"

            if "peer_group_name" in row:
                title += f" ({row['peer_group_name']})"

            plt.title(title)

            plt.tight_layout()

            plt.savefig(

                f"reports/radar_charts/{row['company_id']}_radar.png"

            )

            plt.close()

        print("Radar charts generated.")


if __name__ == "__main__":

    RadarChartGenerator().generate()