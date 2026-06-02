-- ============================================================
-- Financial Transaction Analytics — SQL Query Library
-- Dataset: transactions.csv  (import as table: transactions)
-- Tested dialect: SQLite / DuckDB / SQL Server (ANSI compatible)
-- ============================================================


-- ------------------------------------------------------------
-- 1. TOTAL SPEND BY CATEGORY
--    Ranked highest to lowest; includes transaction count
--    and average transaction value per category.
-- ------------------------------------------------------------
SELECT
    Category,
    COUNT(*)                          AS TransactionCount,
    ROUND(SUM(Amount), 2)             AS TotalSpend,
    ROUND(AVG(Amount), 2)             AS AvgTransactionValue,
    ROUND(SUM(Amount) * 100.0
          / SUM(SUM(Amount)) OVER (), 2) AS PctOfTotalSpend
FROM transactions
GROUP BY Category
ORDER BY TotalSpend DESC;


-- ------------------------------------------------------------
-- 2. MONTHLY SPEND TRENDS
--    Total spend per month with month number for sorting.
-- ------------------------------------------------------------
SELECT
    MonthNum,
    Month,
    COUNT(*)                AS TransactionCount,
    ROUND(SUM(Amount), 2)   AS MonthlySpend,
    ROUND(AVG(Amount), 2)   AS AvgTransactionValue
FROM (
    SELECT *,
           CASE Month
               WHEN 'January'   THEN 1  WHEN 'February'  THEN 2
               WHEN 'March'     THEN 3  WHEN 'April'     THEN 4
               WHEN 'May'       THEN 5  WHEN 'June'      THEN 6
               WHEN 'July'      THEN 7  WHEN 'August'    THEN 8
               WHEN 'September' THEN 9  WHEN 'October'   THEN 10
               WHEN 'November'  THEN 11 WHEN 'December'  THEN 12
           END AS MonthNum
    FROM transactions
) t
GROUP BY MonthNum, Month
ORDER BY MonthNum;


-- ------------------------------------------------------------
-- 3. TOP 10 HIGHEST SINGLE TRANSACTIONS
-- ------------------------------------------------------------
SELECT
    TransactionID,
    Date,
    Month,
    Category,
    MerchantName,
    ROUND(Amount, 2) AS Amount,
    IsAnomaly
FROM transactions
ORDER BY Amount DESC
LIMIT 10;


-- ------------------------------------------------------------
-- 4. ALL ANOMALY-FLAGGED TRANSACTIONS
--    Returns rows marked IsAnomaly = 1 in the source data,
--    ordered by amount descending.
-- ------------------------------------------------------------
SELECT
    TransactionID,
    Date,
    Month,
    Category,
    MerchantName,
    ROUND(Amount, 2) AS Amount
FROM transactions
WHERE IsAnomaly = 1
ORDER BY Amount DESC;


-- ------------------------------------------------------------
-- 5. MONTH-OVER-MONTH SPEND CHANGE BY CATEGORY
--    Uses a self-join to compare each month to the prior month.
--    LAG() variant shown in comment for databases that support it.
-- ------------------------------------------------------------

-- Self-join version (SQLite-compatible):
SELECT
    curr.Category,
    curr.MonthNum,
    curr.Month,
    ROUND(curr.MonthlySpend, 2)                                       AS CurrentMonthSpend,
    ROUND(prev.MonthlySpend, 2)                                       AS PrevMonthSpend,
    ROUND(curr.MonthlySpend - COALESCE(prev.MonthlySpend, 0), 2)      AS MonthChange,
    CASE
        WHEN prev.MonthlySpend IS NULL OR prev.MonthlySpend = 0 THEN NULL
        ELSE ROUND(
            (curr.MonthlySpend - prev.MonthlySpend) / prev.MonthlySpend * 100, 1
        )
    END                                                               AS PctChange
FROM (
    SELECT Category,
           CASE Month
               WHEN 'January'   THEN 1  WHEN 'February'  THEN 2
               WHEN 'March'     THEN 3  WHEN 'April'     THEN 4
               WHEN 'May'       THEN 5  WHEN 'June'      THEN 6
               WHEN 'July'      THEN 7  WHEN 'August'    THEN 8
               WHEN 'September' THEN 9  WHEN 'October'   THEN 10
               WHEN 'November'  THEN 11 WHEN 'December'  THEN 12
           END AS MonthNum,
           Month,
           SUM(Amount) AS MonthlySpend
    FROM transactions
    GROUP BY Category, Month
) curr
LEFT JOIN (
    SELECT Category,
           CASE Month
               WHEN 'January'   THEN 1  WHEN 'February'  THEN 2
               WHEN 'March'     THEN 3  WHEN 'April'     THEN 4
               WHEN 'May'       THEN 5  WHEN 'June'      THEN 6
               WHEN 'July'      THEN 7  WHEN 'August'    THEN 8
               WHEN 'September' THEN 9  WHEN 'October'   THEN 10
               WHEN 'November'  THEN 11 WHEN 'December'  THEN 12
           END AS MonthNum,
           SUM(Amount) AS MonthlySpend
    FROM transactions
    GROUP BY Category, Month
) prev
ON  curr.Category = prev.Category
AND curr.MonthNum  = prev.MonthNum + 1
ORDER BY curr.Category, curr.MonthNum;

/*
-- LAG() version (SQL Server / PostgreSQL / DuckDB):
SELECT
    Category,
    MonthNum,
    Month,
    ROUND(MonthlySpend, 2)                                              AS CurrentMonthSpend,
    ROUND(LAG(MonthlySpend) OVER (PARTITION BY Category ORDER BY MonthNum), 2) AS PrevMonthSpend,
    ROUND(MonthlySpend
          - LAG(MonthlySpend) OVER (PARTITION BY Category ORDER BY MonthNum), 2) AS MonthChange,
    ROUND(
        (MonthlySpend - LAG(MonthlySpend) OVER (PARTITION BY Category ORDER BY MonthNum))
        / NULLIF(LAG(MonthlySpend) OVER (PARTITION BY Category ORDER BY MonthNum), 0) * 100,
    1) AS PctChange
FROM (
    SELECT Category,
           MONTH(CAST(Date AS DATE)) AS MonthNum,
           Month,
           SUM(Amount) AS MonthlySpend
    FROM transactions
    GROUP BY Category, Month, MONTH(CAST(Date AS DATE))
) base
ORDER BY Category, MonthNum;
*/


-- ------------------------------------------------------------
-- 6. SAVINGS OPPORTUNITIES — RANKED BY POTENTIAL SAVING AMOUNT
--    Compares each category's actual annual spend to the
--    spend you would have had without its anomaly transactions.
-- ------------------------------------------------------------
WITH category_totals AS (
    SELECT
        Category,
        SUM(Amount)                                AS TotalAnnualSpend,
        SUM(CASE WHEN IsAnomaly = 0 THEN Amount ELSE 0 END) AS NormalSpend,
        SUM(CASE WHEN IsAnomaly = 1 THEN Amount ELSE 0 END) AS AnomalySpend,
        COUNT(CASE WHEN IsAnomaly = 1 THEN 1 END)           AS AnomalyTransactions
    FROM transactions
    GROUP BY Category
)
SELECT
    Category,
    ROUND(TotalAnnualSpend, 2)   AS TotalAnnualSpend,
    ROUND(NormalSpend,      2)   AS NormalSpend,
    ROUND(AnomalySpend,     2)   AS AnomalySpend,
    AnomalyTransactions,
    ROUND(AnomalySpend * 100.0
          / NULLIF(TotalAnnualSpend, 0), 1) AS AnomalyPct,
    ROUND(AnomalySpend, 2)       AS PotentialAnnualSaving
FROM category_totals
WHERE AnomalySpend > 0
ORDER BY PotentialAnnualSaving DESC;
