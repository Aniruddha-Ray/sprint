PRAGMA foreign_keys = ON;

----------------------------------------------------
-- Companies
----------------------------------------------------

DROP TABLE IF EXISTS companies;

CREATE TABLE companies (

    id TEXT PRIMARY KEY,

    company_logo TEXT,

    company_name TEXT NOT NULL,

    chart_link TEXT,

    about_company TEXT,

    website TEXT,

    nse_profile TEXT,

    bse_profile TEXT,

    face_value REAL,

    book_value REAL,

    roce_percentage REAL,

    roe_percentage REAL

);

----------------------------------------------------
-- Profit & Loss
----------------------------------------------------

DROP TABLE IF EXISTS profitandloss;

CREATE TABLE profitandloss (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    year INTEGER NOT NULL,

    sales REAL,

    expenses REAL,

    operating_profit REAL,

    opm_percentage REAL,

    other_income REAL,

    interest REAL,

    depreciation REAL,

    profit_before_tax REAL,

    tax_percentage REAL,

    net_profit REAL,

    eps REAL,

    dividend_payout REAL,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)

);

----------------------------------------------------
-- Balance Sheet
----------------------------------------------------

DROP TABLE IF EXISTS balancesheet;

CREATE TABLE balancesheet (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    year INTEGER,

    equity_capital REAL,

    reserves REAL,

    borrowings REAL,

    other_liabilities REAL,

    total_liabilities REAL,

    fixed_assets REAL,

    cwip REAL,

    investments REAL,

    other_assets REAL,

    total_assets REAL,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)

);

----------------------------------------------------
-- Cash Flow
----------------------------------------------------

DROP TABLE IF EXISTS cashflow;

CREATE TABLE cashflow (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    year INTEGER,

    operating_activity REAL,

    investing_activity REAL,

    financing_activity REAL,

    net_cash_flow REAL,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)

);

----------------------------------------------------
-- Analysis
----------------------------------------------------

DROP TABLE IF EXISTS analysis;

CREATE TABLE analysis (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    compounded_sales_growth REAL,

    compounded_profit_growth REAL,

    stock_price_cagr REAL,

    roe REAL,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)

);

----------------------------------------------------
-- Documents
----------------------------------------------------

DROP TABLE IF EXISTS documents;

CREATE TABLE documents (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    annual_report TEXT,

    concall_notes TEXT,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)

);

----------------------------------------------------
-- Pros & Cons
----------------------------------------------------

DROP TABLE IF EXISTS prosandcons;

CREATE TABLE prosandcons (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    pros TEXT,

    cons TEXT,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)

);

----------------------------------------------------
-- Financial Ratios
----------------------------------------------------

DROP TABLE IF EXISTS financial_ratios;

CREATE TABLE financial_ratios (

    company_id TEXT NOT NULL,
    year INTEGER NOT NULL,

    ------------------------------------------------
    -- Profitability
    ------------------------------------------------

    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    return_on_capital_employed_pct REAL,
    return_on_assets_pct REAL,

    ------------------------------------------------
    -- Leverage & Efficiency
    ------------------------------------------------

    debt_to_equity REAL,
    interest_coverage REAL,
    icr_label TEXT,
    asset_turnover REAL,

    high_leverage_flag INTEGER DEFAULT 0,
    interest_risk_flag INTEGER DEFAULT 0,

    ------------------------------------------------
    -- Cash Flow KPIs
    ------------------------------------------------

    free_cash_flow_cr REAL,
    cash_from_operations_cr REAL,
    capex_cr REAL,
    fcf_conversion_pct REAL,

    cfo_quality_ratio REAL,
    cfo_quality_label TEXT,

    capital_allocation_pattern TEXT,

    ------------------------------------------------
    -- Per Share
    ------------------------------------------------

    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,

    ------------------------------------------------
    -- Debt
    ------------------------------------------------

    total_debt_cr REAL,

    ------------------------------------------------
    -- Revenue CAGR
    ------------------------------------------------

    revenue_cagr_3yr REAL,
    revenue_cagr_3yr_flag TEXT,

    revenue_cagr_5yr REAL,
    revenue_cagr_5yr_flag TEXT,

    revenue_cagr_10yr REAL,
    revenue_cagr_10yr_flag TEXT,

    ------------------------------------------------
    -- PAT CAGR
    ------------------------------------------------

    pat_cagr_3yr REAL,
    pat_cagr_3yr_flag TEXT,

    pat_cagr_5yr REAL,
    pat_cagr_5yr_flag TEXT,

    pat_cagr_10yr REAL,
    pat_cagr_10yr_flag TEXT,

    ------------------------------------------------
    -- EPS CAGR
    ------------------------------------------------

    eps_cagr_3yr REAL,
    eps_cagr_3yr_flag TEXT,

    eps_cagr_5yr REAL,
    eps_cagr_5yr_flag TEXT,

    eps_cagr_10yr REAL,
    eps_cagr_10yr_flag TEXT,

    ------------------------------------------------
    -- Composite
    ------------------------------------------------

    composite_quality_score REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);

CREATE INDEX IF NOT EXISTS idx_finratio_company
ON financial_ratios(company_id);

CREATE INDEX IF NOT EXISTS idx_finratio_year
ON financial_ratios(year);

CREATE INDEX IF NOT EXISTS idx_finratio_company_year
ON financial_ratios(company_id, year);

----------------------------------------------------
-- Sector Table
----------------------------------------------------

DROP TABLE IF EXISTS sectors;

CREATE TABLE sectors (

    sector_id INTEGER PRIMARY KEY,

    sector_name TEXT

);

----------------------------------------------------
-- Peer Groups
----------------------------------------------------

DROP TABLE IF EXISTS peer_groups;

CREATE TABLE peer_groups (

    company_id TEXT,

    peer_company_id TEXT,

    PRIMARY KEY(company_id, peer_company_id),

    FOREIGN KEY(company_id)

    REFERENCES companies(id),

    FOREIGN KEY(peer_company_id)

    REFERENCES companies(id)

);

----------------------------------------------------
-- Stock Prices
----------------------------------------------------

DROP TABLE IF EXISTS stock_prices;

CREATE TABLE stock_prices (

    company_id TEXT,

    trade_date DATE,

    open REAL,

    high REAL,

    low REAL,

    close REAL,

    volume INTEGER,

    PRIMARY KEY(company_id, trade_date),

    FOREIGN KEY(company_id)

    REFERENCES companies(id)

);