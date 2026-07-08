CREATE TABLE companies(
    id TEXT PRIMARY KEY,
    company_logo TEXT,
    chart_link TEXT,
    company_name TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value INTEGER,
    book_value INTEGER,
    roe_percentage REAL,
    roce_percentage REAL
);

CREATE TABLE profitandloss(
    id INTEGER,
    company_id TEXT,
    year DATE, 
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

DELETE FROM profitandloss 
WHERE company_id NOT IN (SELECT id FROM companies);

CREATE TABLE balancesheet(

    id	INTEGER,
    company_id TEXT,
    year DATE,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL,


    FOREIGN KEY(company_id)

    REFERENCES companies(id)
);

DELETE FROM balancesheet 
WHERE company_id NOT IN (SELECT id FROM companies);

CREATE TABLE cashflow (

    id INTEGER,
    company_id TEXT,
    year DATE
    operating_activity REAL
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)
);

DELETE FROM cashflow 
WHERE company_id NOT IN (SELECT id FROM companies);


CREATE TABLE analysis (

    id INTEGER,
    company_id TEXT,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,
    FOREIGN KEY(company_id)

    REFERENCES companies(id)
);

DELETE FROM analysis 
WHERE company_id NOT IN (SELECT id FROM companies);

CREATE TABLE documents (

    id INTEGER,
    company_id TEXT,
    Year YEAR,
    Annual_Report TEXT,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)
);

DELETE FROM documents 
WHERE company_id NOT IN (SELECT id FROM companies);

CREATE TABLE prosandcons (

    id INTEGER,
    company_id TEXT,
    pros TEXT,
    cons TEXT,

    FOREIGN KEY(company_id)

    REFERENCES companies(id)
);

DELETE FROM prosandcons 
WHERE company_id NOT IN (SELECT id FROM companies);