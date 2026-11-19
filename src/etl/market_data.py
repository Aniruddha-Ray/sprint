"""Sector, peer-group and market data (price, market cap, P/E, P/B).

None of this is in the raw Excel files, so it is built from public NSE files
kept in data/external/ (re-download with `python -m src.etl.market_data`):

  ind_nifty500list.csv             NSE index constituents -> sector ("Industry")
  sec_bhavdata_full_<DDMMYYYY>.csv NSE daily bhavcopy     -> closing price
  sector_overrides.csv             hand-maintained sectors for symbols that
                                   have since left the NSE files

Valuation is struck at the close of PRICE_DATE (last trading day of FY2024)
so it lines up with the latest financial year in the dataset.

Share count = equity capital / face value. Where that is missing or clearly
corrupt in the source (off by >3x from net_profit / EPS), the EPS-implied
count is used instead; `shares_source` records which one.
"""

import sqlite3
import urllib.request

import pandas as pd

from src.etl.config import DATABASE, PROJECT_ROOT

EXTERNAL = PROJECT_ROOT / "data" / "external"

PRICE_DATE = "2024-03-28"

FISCAL_YEAR = 2024

SECTOR_FILE = EXTERNAL / "ind_nifty500list.csv"

PRICE_FILE = EXTERNAL / f"sec_bhavdata_full_{pd.Timestamp(PRICE_DATE):%d%m%Y}.csv"

OVERRIDES_FILE = EXTERNAL / "sector_overrides.csv"

NSE_URLS = {
    SECTOR_FILE: "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
    PRICE_FILE: f"https://nsearchives.nseindia.com/products/content/{PRICE_FILE.name}",
}

FINANCIAL_SECTOR = "Financial Services"


def download(force=False):
    """Fetch the NSE source files into data/external/."""

    EXTERNAL.mkdir(parents=True, exist_ok=True)

    for path, url in NSE_URLS.items():
        if path.exists() and not force:
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            path.write_bytes(resp.read())
        print(f"downloaded {path.name}")


def load_sectors() -> pd.DataFrame:
    """symbol -> broad_sector, NSE list first, overrides on top."""

    nse = pd.read_csv(SECTOR_FILE).rename(columns={"Symbol": "symbol", "Industry": "broad_sector"})

    overrides = pd.read_csv(OVERRIDES_FILE).rename(columns={"industry": "broad_sector"})

    both = pd.concat([nse[["symbol", "broad_sector"]], overrides[["symbol", "broad_sector"]]])

    return both.drop_duplicates("symbol", keep="last")


def load_prices() -> pd.DataFrame:

    df = pd.read_csv(PRICE_FILE, skipinitialspace=True)

    df.columns = df.columns.str.strip()

    df = df[df["SERIES"].str.strip() == "EQ"]

    return pd.DataFrame({
        "symbol": df["SYMBOL"].str.strip(),
        "close_price": pd.to_numeric(df["CLOSE_PRICE"], errors="coerce"),
    })


def nse_symbol(companies: pd.DataFrame) -> pd.Series:
    """The NSE symbol from nse_profile. Not always equal to `id`
    (e.g. id 'ABB' is Abbott India, symbol ABBOTINDIA)."""

    sym = companies["nse_profile"].str.extract(r"symbol=(.+)$")[0].str.strip()

    return sym.fillna(companies["id"])


def build(conn: sqlite3.Connection) -> dict:
    """Populate companies.{nse_symbol,broad_sector,sector_id}, sectors,
    peer_groups and market_data. Returns coverage counts."""

    companies = pd.read_sql("SELECT id, nse_profile, face_value FROM companies", conn)

    companies["nse_symbol"] = nse_symbol(companies)

    df = companies.merge(load_sectors(), left_on="nse_symbol", right_on="symbol", how="left")

    # ---- sectors / companies / peer groups --------------------------------

    sectors = (
        df["broad_sector"].dropna().drop_duplicates().sort_values().reset_index(drop=True)
        .rename("sector_name").to_frame()
    )
    sectors["sector_id"] = sectors.index + 1

    df = df.merge(sectors, left_on="broad_sector", right_on="sector_name", how="left")

    conn.execute("DELETE FROM sectors")
    sectors[["sector_id", "sector_name"]].to_sql("sectors", conn, if_exists="append", index=False)

    conn.executemany(
        "UPDATE companies SET nse_symbol = ?, broad_sector = ?, sector_id = ? WHERE id = ?",
        [
            (r.nse_symbol, r.broad_sector, None if pd.isna(r.sector_id) else int(r.sector_id), r.id)
            for r in df.itertuples()
        ],
    )

    conn.execute("DELETE FROM peer_groups")
    df.dropna(subset=["broad_sector"])[["id", "broad_sector"]].rename(
        columns={"id": "company_id", "broad_sector": "peer_group_name"}
    ).to_sql("peer_groups", conn, if_exists="append", index=False)

    # ---- market data ------------------------------------------------------

    fin = pd.read_sql(
        """
        SELECT p.company_id AS id, p.net_profit, p.eps, b.equity_capital, b.reserves
        FROM profitandloss p
        LEFT JOIN balancesheet b USING (company_id, year)
        WHERE p.year = ?
        """,
        conn,
        params=(FISCAL_YEAR,),
    )

    m = df[["id", "nse_symbol", "face_value"]].merge(fin, on="id", how="left").merge(
        load_prices(), left_on="nse_symbol", right_on="symbol", how="left"
    )

    shares_fv = m["equity_capital"] / m["face_value"]
    shares_eps = (m["net_profit"] / m["eps"]).where(m["eps"] > 0)
    ratio = shares_fv / shares_eps

    use_eps = shares_fv.isna() | ((ratio < 1 / 3) | (ratio > 3)).fillna(False) & shares_eps.notna()

    m["shares_cr"] = shares_fv.where(~use_eps, shares_eps).round(2)
    m["shares_source"] = pd.Series("equity_capital/face_value", index=m.index).where(~use_eps, "net_profit/eps")
    m.loc[m["shares_cr"].isna(), "shares_source"] = None

    m["price_date"] = PRICE_DATE
    m["fiscal_year"] = FISCAL_YEAR
    m["market_cap_cr"] = (m["close_price"] * m["shares_cr"]).round(0)
    m["pe"] = (m["market_cap_cr"] / m["net_profit"]).where(m["net_profit"] > 0).round(2)
    book = m["equity_capital"].fillna(0) + m["reserves"]
    # when equity capital was unusable the book value from the same row is too
    m["pb"] = (m["market_cap_cr"] / book).where((book > 0) & ~use_eps).round(2)

    conn.execute("DELETE FROM market_data")
    m.rename(columns={"id": "company_id"})[
        ["company_id", "price_date", "fiscal_year", "close_price", "shares_cr",
         "shares_source", "market_cap_cr", "pe", "pb"]
    ].to_sql("market_data", conn, if_exists="append", index=False)

    return {
        "companies": len(df),
        "with_sector": int(df["broad_sector"].notna().sum()),
        "with_price": int(m["close_price"].notna().sum()),
        "with_market_cap": int(m["market_cap_cr"].notna().sum()),
        "shares_from_eps": int(use_eps.sum()),
    }


if __name__ == "__main__":

    download(force=True)

    conn = sqlite3.connect(DATABASE)

    try:
        print(build(conn))
        conn.commit()
    finally:
        conn.close()
