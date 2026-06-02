# Power BI Dashboard Guide — Financial Transaction Analytics

## Prerequisites
- Power BI Desktop (free download from microsoft.com/en-us/power-bi)
- `transactions.csv` in a stable folder path
- Basic familiarity with the Power BI canvas

---

## Step 1 — Import transactions.csv

1. Open Power BI Desktop → click **Get data** (Home ribbon).
2. Select **Text/CSV** → navigate to `transactions.csv` → **Open**.
3. In the preview dialog confirm:
   - **Delimiter:** Comma
   - **Data Type Detection:** Based on first 200 rows
4. Click **Transform Data** (not Load) to open Power Query.
5. In Power Query Editor:
   - Verify `Amount` column type is **Decimal Number**.
   - Verify `Date` column type is **Date**.
   - Verify `IsAnomaly` column type is **Whole Number**.
   - Change `MonthNum` column type to **Whole Number** if it appears as text.
6. Click **Close & Apply**.

---

## Step 2 — Create a Date Table (best practice for time intelligence)

In the Home ribbon click **New Table** and paste:

```dax
DateTable =
ADDCOLUMNS(
    CALENDAR(DATE(2024,1,1), DATE(2024,12,31)),
    "Year",        YEAR([Date]),
    "MonthNum",    MONTH([Date]),
    "MonthName",   FORMAT([Date], "MMMM"),
    "ShortMonth",  FORMAT([Date], "MMM"),
    "Quarter",     "Q" & QUARTER([Date])
)
```

Then go to **Model view** and draw a relationship:
- `DateTable[Date]` → `transactions[Date]`  (Many-to-one, single direction)

---

## Step 3 — DAX Measures

Click **New Measure** on the `transactions` table for each measure below.

### Measure 1 — Total Spend
```dax
Total Spend =
SUM(transactions[Amount])
```
**Format:** Currency, 2 decimal places.

### Measure 2 — Anomaly Count
```dax
Anomaly Count =
CALCULATE(
    COUNTROWS(transactions),
    transactions[IsAnomaly] = 1
)
```
**Format:** Whole number, no decimal.

### Measure 3 — Projected Annual Savings
```dax
Projected Annual Savings =
VAR SavingsRate = SELECTEDVALUE('SavingsParameter'[SavingsParameter Value], 0.10)
VAR AnomalySpend =
    CALCULATE(
        SUM(transactions[Amount]),
        transactions[IsAnomaly] = 1
    )
RETURN
    ROUND(AnomalySpend * SavingsRate, 2)
```
**Format:** Currency, 2 decimal places.  
*(The `SavingsParameter` table is created in Step 4 — build it before using this measure.)*

---

## Step 4 — What-If Savings Parameter (Numeric Range Slicer)

1. Go to **Modeling** ribbon → **New Parameter** → **Numeric Range**.
2. Set:
   | Field | Value |
   |---|---|
   | Name | `SavingsParameter` |
   | Minimum | `0.05` |
   | Maximum | `0.50` |
   | Increment | `0.05` |
   | Default | `0.10` |
3. Click **OK**. Power BI creates a table and a slicer visual automatically.
4. Rename the slicer title to **"Savings Rate (%)"** in the Format pane → rename the slicer header.
5. In the slicer Format pane → **Slider** style.

---

## Step 5 — Build the 5 Visuals

### Visual 1 — Spend by Category Bar Chart

| Setting | Value |
|---|---|
| Visual type | Clustered bar chart |
| Y-axis (field) | `transactions[Category]` |
| X-axis (field) | `[Total Spend]` measure |
| Sort | Sort by Total Spend, descending |
| Data labels | On, format `$#,0` |
| Title | "Annual Spend by Category" |
| X-axis title | "Total Spend ($)" |
| Color | Use "Category" in Legend or set a single theme color |

**Formatting tips:**
- Format pane → X axis → Display units: **Thousands (K)** or **None** (for exact labels).
- Remove gridlines for a cleaner look: Format → Grid lines → Off.

---

### Visual 2 — Monthly Spend Trend Line Chart

| Setting | Value |
|---|---|
| Visual type | Line chart |
| X-axis | `DateTable[MonthName]` |
| Y-axis | `[Total Spend]` measure |
| Sort X-axis | Sort by `DateTable[MonthNum]` ascending |
| Markers | On |
| Data labels | On, position Above |
| Title | "Monthly Spend Trend — 2024" |

**Formatting tips:**
- Drag `DateTable[MonthNum]` to the **Sort by** field of the X-axis (not as a visible field, just for sorting).
- In Format pane → Line → Stroke width: **2.5 pt**.
- Add a constant line at the average: Analytics pane → **Average line** → label it "Monthly avg".

---

### Visual 3 — Anomaly Table

| Setting | Value |
|---|---|
| Visual type | Table |
| Columns | `Date`, `Category`, `MerchantName`, `Amount`, `IsAnomaly` |
| Filter | `IsAnomaly` = 1 (add a page-level or visual-level filter) |
| Conditional formatting | `Amount` column → Background color scale (white → red) |
| Title | "Flagged Anomalous Transactions" |

**Formatting tips:**
- Format pane → Style presets: **Alternating rows** for readability.
- Format `Amount` as Currency (`$#,0.00`).
- Sort by Amount descending by default.

---

### Visual 4 — Savings Opportunity Chart

| Setting | Value |
|---|---|
| Visual type | Clustered bar chart |
| Y-axis | `transactions[Category]` |
| X-axis | Custom measure (see below) |
| Title | "Savings Opportunity by Category" |

Create an additional measure:

```dax
Anomaly Spend =
CALCULATE(
    SUM(transactions[Amount]),
    transactions[IsAnomaly] = 1
)
```

Use `[Anomaly Spend]` on the X-axis.

**Formatting tips:**
- Apply conditional formatting → Data bars to X-axis for visual emphasis.
- Add a data label: Format → Data labels → On, format `$#,0`.
- Highlight the top-2 bars: use a calculated column `TopCategory` and color-code by it.

**Top 2 calculated column (add to transactions table):**
```dax
TopCategory =
VAR Cat = transactions[Category]
VAR RankedCats =
    TOPN(2,
         SUMMARIZE(
             ALL(transactions),
             transactions[Category],
             "AnomalySpend", CALCULATE(SUM(transactions[Amount]), transactions[IsAnomaly] = 1)
         ),
         [AnomalySpend], DESC
    )
RETURN
    IF(Cat IN SELECTCOLUMNS(RankedCats, "Category", transactions[Category]),
       "Top Overspend", "Other")
```
Then set bar color by `TopCategory` (Top Overspend → Gold, Other → Steel blue).

---

### Visual 5 — What-If Savings Simulator Card

| Setting | Value |
|---|---|
| Visual type | Card |
| Field | `[Projected Annual Savings]` measure |
| Title | "Projected Annual Savings" |
| Data label format | Currency, 0 decimal places |

Place this card beside the `SavingsParameter` slicer created in Step 4.  
Moving the slicer updates the card in real time — this is the simulator.

**Optional enhancement:** Add a second card with `[Anomaly Count]` and a third with `[Total Spend]` to form a KPI strip at the top of the page.

---

## Step 6 — Page Layout & Final Formatting

### Recommended layout (1280 × 720 canvas)

```
┌─────────────────────────────────────────────────────────────────┐
│  [Card: Total Spend]  [Card: Anomaly Count]  [Card: Savings]    │
├───────────────────────┬─────────────────────────────────────────┤
│                       │                                         │
│  Visual 1             │  Visual 2                               │
│  Spend by Category    │  Monthly Trend Line                     │
│                       │                                         │
├───────────────────────┼─────────────────────────────────────────┤
│  Visual 4             │  Visual 3                               │
│  Savings Opportunity  │  Anomaly Table                          │
│                       │                                         │
├───────────────────────┴─────────────────────────────────────────┤
│  [SavingsRate Slicer ◄──►]   [Card: Projected Annual Savings]   │
└─────────────────────────────────────────────────────────────────┘
```

### Theme & formatting tips
- **Theme:** View ribbon → Themes → **Executive** or import a custom JSON theme.
- **Background:** Format pane on each visual → set a light gray (`#F5F5F5`) card background.
- **Font:** Segoe UI, 11pt for labels, 13pt bold for titles.
- **Title bar:** Insert a text box at the top reading "Financial Transaction Analytics Dashboard — 2024" in 18pt bold.

---

## Step 7 — Publish (Optional)

1. Save the `.pbix` file.
2. Home ribbon → **Publish** → sign in to Power BI service.
3. Choose your workspace → **Select**.
4. Once published, open the report in your browser and pin visuals to a dashboard for sharing.

---

## Quick Reference — Field Mappings

| Visual | Power BI Field Well | Source Column / Measure |
|---|---|---|
| Bar Chart | Y-axis | `transactions[Category]` |
| Bar Chart | X-axis | `[Total Spend]` |
| Line Chart | X-axis | `DateTable[MonthName]` (sorted by `MonthNum`) |
| Line Chart | Y-axis | `[Total Spend]` |
| Anomaly Table | Columns | `Date`, `Category`, `MerchantName`, `Amount`, `IsAnomaly` |
| Anomaly Table | Filter | `IsAnomaly = 1` |
| Savings Chart | Y-axis | `transactions[Category]` |
| Savings Chart | X-axis | `[Anomaly Spend]` |
| Savings Card | Value | `[Projected Annual Savings]` |
| Slicer | Field | `SavingsParameter[SavingsParameter Value]` |
