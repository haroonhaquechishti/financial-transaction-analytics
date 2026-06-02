import csv
import random
import math
from datetime import date, timedelta

random.seed(42)

# Each category defines: base monthly spend, std dev, per-month seasonal multipliers,
# and min/max number of individual transactions to split that budget into.
CATEGORIES = {
    "Housing":       {"base": 1500, "std": 80,  "txn_range": (3,   6),  "seasonal": [1.0]*12},
    "Food":          {"base": 620,  "std": 70,  "txn_range": (120, 160),"seasonal": [0.95,0.93,0.97,1.00,1.05,1.10,1.12,1.08,1.02,1.00,1.10,1.20]},
    "Transport":     {"base": 310,  "std": 50,  "txn_range": (85,  115),"seasonal": [1.05,1.03,1.00,0.98,0.97,0.95,0.96,0.97,1.00,1.02,1.04,1.08]},
    "Entertainment": {"base": 210,  "std": 55,  "txn_range": (35,  55), "seasonal": [0.85,0.88,0.92,1.00,1.10,1.20,1.25,1.20,1.05,1.00,1.15,1.35]},
    "Shopping":      {"base": 480,  "std": 110, "txn_range": (70,  100),"seasonal": [1.30,0.75,0.80,0.85,0.90,0.90,0.95,0.95,0.95,1.05,1.40,1.80]},
    "Health":        {"base": 220,  "std": 65,  "txn_range": (25,  40), "seasonal": [1.10,1.08,1.05,1.00,0.97,0.95,0.93,0.94,0.98,1.02,1.06,1.10]},
    "Utilities":     {"base": 185,  "std": 35,  "txn_range": (12,  20), "seasonal": [1.25,1.20,1.05,0.90,0.80,0.82,0.85,0.88,0.90,1.00,1.15,1.25]},
    "Subscriptions": {"base": 95,   "std": 12,  "txn_range": (12,  18), "seasonal": [1.0]*12},
}

MERCHANTS = {
    "Housing":       ["Sunshine Apartments","Greenview Property Mgmt","Metro Realty","Riverside Rentals","City Home LLC","Oakwood Leasing"],
    "Food":          ["Whole Foods","Trader Joe's","Chipotle","Panera Bread","Domino's","Subway","McDonald's","Starbucks",
                      "Local Bistro","FreshMart","Safeway","Kroger","Panda Express","Shake Shack","Five Guys",
                      "Olive Garden","Chili's","Jersey Mike's","Dunkin'","Tim Hortons"],
    "Transport":     ["Shell Gas","BP Fuel","Uber","Lyft","Metro Transit","ParkNow","EZPass Toll","Chevron",
                      "Circle K","Sunoco","Valero","SpeedyPark","Hertz","Enterprise","Zipcar"],
    "Entertainment": ["Netflix","AMC Theaters","Spotify","Steam","Hulu","Ticketmaster","ESPN+",
                      "Dave & Buster's","Bowling Alley","Regal Cinemas","Live Nation","Disney+","HBO Max","Apple TV+"],
    "Shopping":      ["Amazon","Target","Walmart","Best Buy","H&M","Nike Store","IKEA","Macy's","eBay","Etsy",
                      "Costco","TJ Maxx","Nordstrom","Gap","Old Navy","Zara","HomeDepot","Lowe's","PetSmart"],
    "Health":        ["CVS Pharmacy","Walgreens","Planet Fitness","Gold's Gym","Dr. Smith MD",
                      "Dental Care Plus","Vision Works","Urgent Care","Rite Aid","Anytime Fitness","Mayo Clinic Portal"],
    "Utilities":     ["City Electric Co","Natural Gas LLC","Water Dept","Internet Pro","Xfinity","AT&T","Spectrum","Verizon","T-Mobile"],
    "Subscriptions": ["Adobe CC","Microsoft 365","Apple One","YouTube Premium","Amazon Prime",
                      "Dropbox","LinkedIn Premium","Grammarly","Notion","LastPass","Canva Pro"],
}

MONTH_NAMES = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]

def days_in_month(year, month):
    if month in (1,3,5,7,8,10,12): return 31
    if month in (4,6,9,11): return 30
    return 29 if year % 4 == 0 else 28

def generate_normal_transactions(year=2024):
    transactions = []
    txn_id = 1

    for month_idx in range(12):
        month_num = month_idx + 1
        dim = days_in_month(year, month_num)
        mo_name = MONTH_NAMES[month_idx]

        for category, cfg in CATEGORIES.items():
            seasonal_factor = cfg["seasonal"][month_idx]
            monthly_budget = cfg["base"] * seasonal_factor
            std = cfg["std"]
            lo, hi = cfg["txn_range"]
            num_txns = random.randint(lo, hi)

            amounts = [max(1.5, random.gauss(monthly_budget / num_txns, std / num_txns * 1.5))
                       for _ in range(num_txns)]
            # Scale amounts so they sum close to monthly_budget
            total = sum(amounts)
            amounts = [round(a / total * monthly_budget, 2) for a in amounts]

            for amount in amounts:
                amount = max(1.50, amount)
                day = random.randint(1, dim)
                txn_date = date(year, month_num, day)
                merchant = random.choice(MERCHANTS[category])

                transactions.append({
                    "TransactionID": f"TXN{txn_id:05d}",
                    "Date": txn_date.strftime("%Y-%m-%d"),
                    "Month": mo_name,
                    "Category": category,
                    "Amount": amount,
                    "MerchantName": merchant,
                    "IsAnomaly": 0,
                })
                txn_id += 1

    return transactions, txn_id


def inject_anomalies(start_id, year=2024, target=37):
    """Generate exactly `target` anomalous transactions with large spike amounts."""
    anomalies = []
    txn_id = start_id

    # (category, month_num, month_name, amt_low, amt_high, merchant, count)
    spike_templates = [
        ("Food",          2,  "February",  750, 920,  "Whole Foods",         3),
        ("Food",          7,  "July",      800, 980,  "Local Bistro",        3),
        ("Food",          11, "November",  820, 1010, "Chipotle",            3),
        ("Shopping",      1,  "January",  1600, 2100, "Amazon",              4),
        ("Shopping",      11, "November", 2000, 2500, "Best Buy",            4),
        ("Shopping",      12, "December", 2200, 2800, "Amazon",              4),
        ("Entertainment", 7,  "July",      600,  780, "Ticketmaster",        3),
        ("Entertainment", 12, "December",  680,  850, "AMC Theaters",        3),
        ("Health",        1,  "January",   620,  800, "Dr. Smith MD",        3),
        ("Health",        3,  "March",     700,  890, "Dental Care Plus",    3),
        ("Transport",     6,  "June",      490,  630, "Uber",                3),
        ("Utilities",     1,  "January",   400,  510, "City Electric Co",    3),
    ]

    for cat, mo, mo_name, amt_lo, amt_hi, merchant, count in spike_templates:
        dim = days_in_month(year, mo)
        for _ in range(count):
            day = random.randint(1, dim)
            txn_date = date(year, mo, day)
            amount = round(random.uniform(amt_lo, amt_hi), 2)
            anomalies.append({
                "TransactionID": f"TXN{txn_id:05d}",
                "Date": txn_date.strftime("%Y-%m-%d"),
                "Month": mo_name,
                "Category": cat,
                "Amount": amount,
                "MerchantName": merchant,
                "IsAnomaly": 1,
            })
            txn_id += 1

    # total from templates = 3+3+3+4+4+4+3+3+3+3+3+3 = 39 — trim to exactly target
    random.shuffle(anomalies)
    anomalies = anomalies[:target]

    # Re-stamp IDs sequentially from start_id
    for i, a in enumerate(anomalies):
        a["TransactionID"] = f"TXN{start_id + i:05d}"

    return anomalies


def main():
    print("Generating synthetic transaction dataset...")
    normal_txns, next_id = generate_normal_transactions(2024)
    print(f"  Normal transactions generated : {len(normal_txns):,}")

    anomalies = inject_anomalies(next_id, 2024, target=37)
    print(f"  Anomalous transactions injected: {len(anomalies)}")

    all_txns = normal_txns + anomalies
    all_txns.sort(key=lambda x: x["Date"])

    # Re-assign clean sequential IDs after sort
    for i, t in enumerate(all_txns, start=1):
        t["TransactionID"] = f"TXN{i:05d}"

    output_file = "transactions.csv"
    fieldnames = ["TransactionID", "Date", "Month", "Category", "Amount", "MerchantName", "IsAnomaly"]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_txns)

    total = len(all_txns)
    actual_anomalies = sum(1 for t in all_txns if t["IsAnomaly"] == 1)
    total_spend = sum(t["Amount"] for t in all_txns)

    print(f"\n--- Dataset Summary ---")
    print(f"  Output file   : {output_file}")
    print(f"  Total records : {total:,}")
    print(f"  Normal        : {total - actual_anomalies:,}")
    print(f"  Anomalies     : {actual_anomalies}")
    print(f"  Total spend   : ${total_spend:,.2f}")
    print(f"  Date range    : 2024-01-01 to 2024-12-31")
    print("Done.")


if __name__ == "__main__":
    main()
