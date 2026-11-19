"""Financial ratio engine: builds the financial_ratios table.

Run from the repository root, after the ETL load:

    python -m src.analytics.ratio_engine
"""

from __future__ import annotations

import logging
import sqlite3

import pandas as pd

from src.analytics.cagr import INSUFFICIENT, calculate_cagr
from src.analytics.cashflow_kpis import (
    capex_amount,
    capex_intensity,
    capex_label,
    capital_allocation_pattern,
    cfo_quality_label,
    cfo_quality_ratio,
    fcf_conversion,
    free_cash_flow,
)
from src.analytics.ratios import (
    asset_turnover,
    book_value_per_share,
    composite_quality_score,
    debt_to_equity,
    earnings_per_share,
    high_leverage_flag,
    icr_label,
    interest_coverage_ratio,
    interest_risk_flag,
    net_profit_margin,
    operating_profit_margin,
    return_on_assets,
    return_on_capital_employed,
    return_on_equity,
)
from src.etl.config import DATABASE, OUTPUT

EDGE_CASE_LOG = OUTPUT / "ratio_edge_cases.log"

logger = logging.getLogger(__name__)

CAGR_WINDOWS = (3, 5, 10)


def _num(value):
    """NaN/None -> None so ratio functions never see NaN."""
    return None if value is None or pd.isna(value) else float(value)


class DatabaseManager:

    def __init__(self, db_path=DATABASE):

        self.conn = sqlite3.connect(db_path)

    def close(self):

        self.conn.close()

    def load_tables(self):

        q = lambda sql: pd.read_sql(sql, self.conn)  # noqa: E731

        return {
            "companies": q(
                "SELECT id AS company_id, face_value, roe_percentage, roce_percentage, broad_sector FROM companies"
            ),
            "profit": q("SELECT * FROM profitandloss").drop(columns="id"),
            "balance": q("SELECT * FROM balancesheet").drop(columns="id"),
            "cash": q("SELECT * FROM cashflow").drop(columns="id"),
        }


class DataPreprocessor:

    @staticmethod
    def merge_tables(data):

        # P&L drives the row set; balance sheet / cash flow can be missing for
        # some years and must not silently drop the whole company-year.
        df = (
            data["profit"]
            .merge(data["balance"], on=["company_id", "year"], how="left")
            .merge(data["cash"], on=["company_id", "year"], how="left")
            .merge(data["companies"], on="company_id", how="left")
        )

        return df.sort_values(["company_id", "year"]).reset_index(drop=True)


class RatioCalculator:

    @staticmethod
    def compute_basic_ratios(df: pd.DataFrame) -> pd.DataFrame:

        records = []

        for row in df.to_dict("records"):

            r = {k: v if isinstance(v, str) else _num(v) for k, v in row.items()}

            # Source balance sheets for a few companies (BEL, HAL, INDIGO, LT) are
            # implausible: total assets <20% of sales (real companies here are >=40%). Ratios built
            # on them (ROE in the 1000s of %) are dropped rather than reported.
            if r.get("total_assets") is not None and r.get("sales") and r["total_assets"] < 0.2 * r["sales"]:
                logger.warning(
                    "[BALANCE SHEET] %s %s total_assets=%s vs sales=%s - balance-sheet ratios skipped",
                    r["company_id"], r["year"], r["total_assets"], r["sales"],
                )
                for col in ("equity_capital", "reserves", "borrowings", "total_assets"):
                    r[col] = None

            def has(*cols):
                return all(r.get(c) is not None for c in cols)

            npm = net_profit_margin(r["net_profit"], r["sales"])

            opm = operating_profit_margin(r["operating_profit"], r["sales"])

            roe = return_on_equity(r["net_profit"], r["equity_capital"], r["reserves"]) \
                if has("net_profit", "equity_capital", "reserves") else None

            roce = return_on_capital_employed(
                r["profit_before_tax"], r["interest"], r["equity_capital"], r["reserves"], r["borrowings"]
            ) if has("profit_before_tax", "interest", "equity_capital", "reserves", "borrowings") else None

            roa = return_on_assets(r["net_profit"], r["total_assets"]) \
                if has("net_profit", "total_assets") else None

            de = debt_to_equity(r["borrowings"], r["equity_capital"], r["reserves"]) \
                if has("borrowings", "equity_capital", "reserves") else None

            icr = interest_coverage_ratio(r["operating_profit"], r["other_income"], r["interest"]) \
                if has("operating_profit", "other_income", "interest") else None

            turnover = asset_turnover(r["sales"], r["total_assets"]) if has("sales", "total_assets") else None

            face_value = r["face_value"] or 10

            eps = earnings_per_share(r["net_profit"], r["equity_capital"], face_value) \
                if has("net_profit", "equity_capital") else None

            bvps = book_value_per_share(r["equity_capital"], r["reserves"], face_value) \
                if has("equity_capital", "reserves") else None

            # dividend_payout in the source is already a percentage of profit.
            # Negative values (e.g. -999) are placeholders for "not available".
            payout = r["dividend_payout"]
            payout = payout if payout is not None and payout >= 0 else None

            records.append({
                **row,
                "net_profit_margin_pct": npm,
                "operating_profit_margin_pct": opm,
                "return_on_equity_pct": roe,
                "return_on_capital_employed_pct": roce,
                "return_on_assets_pct": roa,
                "debt_to_equity": de,
                "interest_coverage": icr,
                "icr_label": icr_label(r["interest"], icr) if r["interest"] is not None else None,
                "asset_turnover": turnover,
                "earnings_per_share": eps,
                "book_value_per_share": bvps,
                "dividend_payout_ratio_pct": payout,
                "total_debt_cr": r["borrowings"],
                "composite_quality_score": composite_quality_score(roe, roce, npm, de, icr, turnover),
                # banks / NBFCs run high D/E by design, so Financial Services is exempt
                "high_leverage_flag": int(high_leverage_flag(de, r.get("broad_sector"))),
                "interest_risk_flag": int(interest_risk_flag(icr)),
            })

        return pd.DataFrame(records)


class CAGRCalculator:

    SERIES = {"revenue": "sales", "pat": "net_profit", "eps": "eps"}

    @staticmethod
    def compute(df: pd.DataFrame) -> pd.DataFrame:
        """CAGR over N *calendar* years (looked up by year, not by row
        position, so gaps in the history don't produce wrong windows)."""

        result = []

        for _, group in df.groupby("company_id", sort=False):

            group = group.sort_values("year").copy()

            for prefix, col in CAGRCalculator.SERIES.items():

                by_year = dict(zip(group["year"], group[col]))

                for window in CAGR_WINDOWS:

                    values, flags = [], []

                    for year, end in zip(group["year"], group[col]):

                        if year - window not in by_year:
                            values.append(None)
                            flags.append(INSUFFICIENT)
                            continue

                        value, flag = calculate_cagr(by_year[year - window], end, window)
                        values.append(value)
                        flags.append(flag)

                    group[f"{prefix}_cagr_{window}yr"] = values
                    group[f"{prefix}_cagr_{window}yr_flag"] = flags

            result.append(group)

        return pd.concat(result, ignore_index=True)


class CashFlowCalculator:

    @staticmethod
    def compute(df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

        cfo = df["operating_activity"].map(_num)
        cfi = df["investing_activity"].map(_num)
        cff = df["financing_activity"].map(_num)

        fcf = [free_cash_flow(o, i) for o, i in zip(cfo, cfi)]
        cfo_ratio = [cfo_quality_ratio(o, p) for o, p in zip(cfo, df["net_profit"].map(_num))]

        df["free_cash_flow_cr"] = fcf
        df["cash_from_operations_cr"] = cfo
        df["capex_cr"] = cfi.map(capex_amount)
        df["fcf_conversion_pct"] = [fcf_conversion(f, op) for f, op in zip(fcf, df["operating_profit"].map(_num))]
        df["cfo_quality_ratio"] = cfo_ratio
        df["cfo_quality_label"] = [cfo_quality_label(x) for x in cfo_ratio]
        df["capital_allocation_pattern"] = [
            capital_allocation_pattern(o, i, f, q) for o, i, f, q in zip(cfo, cfi, cff, cfo_ratio)
        ]
        df["capex_category"] = [
            capex_label(capex_intensity(i, s)) for i, s in zip(cfi, df["sales"].map(_num))
        ]

        return df


class SQLiteWriter:

    def __init__(self, conn: sqlite3.Connection):

        self.conn = conn

    def table_columns(self):

        cols = [r[1] for r in self.conn.execute("PRAGMA table_info('financial_ratios')")]

        if not cols:
            raise RuntimeError(
                "financial_ratios table is missing - run `python -m src.etl.load_database` first."
            )

        return cols

    def save(self, df: pd.DataFrame):
        """Replace the contents of financial_ratios (schema, indexes and FKs are kept)."""

        cols = self.table_columns()

        self.conn.execute("PRAGMA foreign_keys = ON")

        try:
            self.conn.execute("DELETE FROM financial_ratios")

            df.reindex(columns=cols).to_sql("financial_ratios", self.conn, if_exists="append", index=False)

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

        logger.info("financial_ratios rows inserted: %d", len(df))

    def verify(self):

        count = self.conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]

        logger.info("financial_ratios row count = %d", count)

        return count

    def foreign_key_check(self):

        result = pd.read_sql("PRAGMA foreign_key_check;", self.conn)

        if len(result):
            logger.warning("Foreign key violations detected: %d", len(result))
        else:
            logger.info("Foreign key check PASSED.")

        return result

    def vacuum(self):

        self.conn.execute("VACUUM")


class ReportGenerator:

    def __init__(self):

        self.output_dir = OUTPUT

    def generate_capital_allocation(self, df):

        cols = [c for c in ["company_id", "year", "capital_allocation_pattern"] if c in df.columns]

        df[cols].to_csv(self.output_dir / "capital_allocation.csv", index=False)

    def check_ratio_mismatch(self, df):
        """Compare the latest computed ROE/ROCE with the values quoted in companies."""

        logger.info("----- Ratio Cross Check (latest year vs companies sheet) -----")

        latest = df.loc[df.groupby("company_id")["year"].idxmax()]

        for src_col, calc_col, label in [
            ("roe_percentage", "return_on_equity_pct", "ROE"),
            ("roce_percentage", "return_on_capital_employed_pct", "ROCE"),
        ]:
            diff = (latest[src_col] - latest[calc_col]).abs()

            for _, row in latest[diff > 5].iterrows():
                logger.warning(
                    "[%s] %s %s quoted=%s computed=%s",
                    label, row["company_id"], row["year"], row[src_col], row[calc_col],
                )

    def check_cagr_flags(self, df):

        logger.info("----- CAGR Flags -----")

        flag_cols = [c for c in df.columns if c.endswith("_flag") and "cagr" in c]

        counts = df[flag_cols].stack().value_counts()

        for flag, n in counts.items():
            logger.info("%s: %d", flag, n)

    def generate(self, df):

        self.generate_capital_allocation(df)

        self.check_ratio_mismatch(df)

        self.check_cagr_flags(df)

        logger.info("High leverage rows: %d", int(df["high_leverage_flag"].sum()))

        logger.info("Interest risk rows: %d", int(df["interest_risk_flag"].sum()))

        logger.info("----- Missing Values -----")

        for col, cnt in df.isna().sum().items():
            if cnt:
                logger.info("%s: %d", col, cnt)


def build_ratios(db_path=DATABASE) -> pd.DataFrame:

    db = DatabaseManager(db_path)

    try:
        merged = DataPreprocessor.merge_tables(db.load_tables())

        ratio_df = RatioCalculator.compute_basic_ratios(merged)

        ratio_df = CAGRCalculator.compute(ratio_df)

        ratio_df = CashFlowCalculator.compute(ratio_df)

        writer = SQLiteWriter(db.conn)

        writer.save(ratio_df)

        rows = writer.verify()

        fk = writer.foreign_key_check()

        writer.vacuum()

    finally:
        db.close()

    return ratio_df, rows, fk


def main():

    OUTPUT.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=EDGE_CASE_LOG,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger.info("Starting Financial Ratio Engine")

    ratio_df, rows, fk = build_ratios()

    ReportGenerator().generate(ratio_df)

    print("=" * 60)
    print("Financial Ratio Engine Completed")
    print(f"Rows inserted : {rows}")
    print(f"FK violations : {len(fk)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
