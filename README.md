# Financial Transaction Analytics & Anomaly Detection

## Project Overview
Most people have no idea where their money actually goes. This project processes 5,000+ financial transactions to uncover spending patterns, build an interactive savings simulator, and automatically flag anomalous transactions — putting the power of financial intelligence into a simple Power BI dashboard.

## Business Problem
Two questions drive this project:
1. **Where is money being wasted?** — Category-level spending analysis with savings opportunity identification
2. **What looks unusual?** — Anomaly detection to surface irregular or potentially fraudulent transactions

## Dataset
- 5,000+ synthetic credit card transactions across 12 months
- Features: transaction date, merchant, category, amount, frequency
- 8 spending categories: Housing, Food, Transport, Entertainment, Shopping, Health, Utilities, Subscriptions

## Methodology

### Step 1 — Data Cleaning & Categorization (Python + SQL)
- Loaded raw transaction data using Pandas
- Cleaned missing values, standardized merchant names, parsed dates
- Categorized all transactions into 8 business-relevant buckets using SQL classification logic

### Step 2 — Anomaly Detection (Python)
Applied statistical anomaly detection to flag irregular transactions:
- Calculated rolling mean and standard deviation per category
- Flagged transactions exceeding 2.5 standard deviations from category baseline
- Result: **37 irregular transactions flagged** across the 12-month period
- Anomaly types detected: unusual single-transaction amounts, off-pattern timing, duplicate-like charges

### Step 3 — Savings Analysis (Python)
- Identified spending categories with highest month-over-month variance
- Calculated discretionary vs. non-discretionary spend ratio
- Pinpointed **$4,200 in annual savings opportunities** across recurring discretionary categories

### Step 4 — Interactive Dashboard (Power BI)
- Monthly burn rate by category with trend lines
- **What-if savings simulator** — interactive sliders let users adjust spending by category and see projected annual savings update in real time
- Anomaly flag panel — highlighted transactions with deviation scores
- Built for non-technical stakeholders — no data literacy required to use

## Key Findings
- Top overspend categories: Entertainment (+34% above baseline) and Subscriptions (+28%)
- 37 transactions flagged as anomalous — 12 identified as likely duplicate charges
- Reducing discretionary spend to category averages yields $4,200/year in savings

## Business Impact
- **$4,200 in identified annual savings opportunities**
- **37 irregular transactions flagged** via automated anomaly detection
- Interactive simulator enables real-time financial planning without spreadsheets

## Tools & Technologies
- **Python** — data cleaning, categorization, anomaly detection (Pandas, NumPy, SciPy)
- **SQL** — transaction classification and aggregation queries
- **Power BI** — interactive dashboard and what-if simulator

## Files
```
financial-transaction-analytics/
├── data/               # Synthetic transaction dataset (CSV)
├── sql/                # SQL categorization and aggregation queries
├── notebooks/          # Python cleaning and anomaly detection
├── dashboard/          # Power BI .pbix file
├── screenshots/        # Dashboard screenshots
└── README.md
```

## How to Run
1. Clone the repository
2. Run the Jupyter notebook in `/notebooks` for data cleaning and anomaly detection
3. Run SQL scripts in `/sql` for aggregations
4. Open `/dashboard/transaction_dashboard.pbix` in Power BI Desktop
