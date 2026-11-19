SELECT COUNT(*) AS total_companies
FROM companies;

SELECT
    s.sector_name,
    COUNT(*) AS total_companies
FROM companies c
JOIN sectors s
ON c.sector_id = s.sector_id
GROUP BY s.sector_name
ORDER BY total_companies DESC;

SELECT
company_id,
MAX(year) AS latest_year,
MAX(sales) AS latest_sales
FROM profitandloss
GROUP BY company_id;

SELECT
company_id,
year,
sales
FROM profitandloss
ORDER BY sales DESC
LIMIT 10;

SELECT AVG(return_on_equity_pct) AS average_roe
FROM financial_ratios;

SELECT
company_id,
MAX(trade_date)
FROM stock_prices
GROUP BY company_id;

SELECT c.company_name
FROM companies c
LEFT JOIN profitandloss p
ON c.id=p.company_id
WHERE p.company_id IS NULL;

SELECT COUNT(*) FROM companies;

SELECT COUNT(*) FROM profitandloss;

SELECT COUNT(*) FROM balancesheet;

SELECT COUNT(*) FROM cashflow;

SELECT COUNT(*) FROM stock_prices;


SELECT *
FROM profitandloss
ORDER BY net_profit DESC
LIMIT 10;


SELECT *
FROM financial_ratios
ORDER BY debt_to_equity DESC
LIMIT 10;