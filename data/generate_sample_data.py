"""
Generates a synthetic Superstore-like dataset and loads it into DuckDB.
Called automatically on first startup if superstore.db is missing.
"""

import os
import random
import duckdb
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "superstore.db")

REGIONS      = ["West", "East", "Central", "South"]
STATES       = {
    "West":    ["California", "Washington", "Oregon", "Nevada", "Utah"],
    "East":    ["New York", "Pennsylvania", "Ohio", "Virginia", "Florida"],
    "Central": ["Texas", "Illinois", "Michigan", "Missouri", "Wisconsin"],
    "South":   ["Georgia", "North Carolina", "Tennessee", "Alabama", "Louisiana"],
}
CITIES       = ["Los Angeles", "Seattle", "New York", "Chicago", "Houston",
                "Atlanta", "Philadelphia", "Phoenix", "San Diego", "Dallas"]
SEGMENTS     = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES   = ["Standard Class", "Second Class", "First Class", "Same Day"]
CATEGORIES   = {
    "Furniture":       ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Envelopes", "Labels", "Fasteners",
                        "Supplies", "Art", "Accessories", "Storage"],
    "Technology":      ["Phones", "Copiers", "Machines", "Accessories"],
}
CUSTOMERS = [f"Customer_{i:04d}" for i in range(1, 201)]


def _rand_date(year: int) -> str:
    month = random.randint(1, 12)
    day   = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generate(n_rows: int = 5000, seed: int = 42) -> None:
    random.seed(seed)
    rows = []
    for i in range(n_rows):
        region   = random.choice(REGIONS)
        state    = random.choice(STATES[region])
        city     = random.choice(CITIES)
        segment  = random.choice(SEGMENTS)
        category = random.choice(list(CATEGORIES.keys()))
        sub_cat  = random.choice(CATEGORIES[category])
        year     = random.randint(2014, 2017)
        order_date = _rand_date(year)
        ship_date  = _rand_date(year)
        customer   = random.choice(CUSTOMERS)
        sales      = round(random.uniform(10, 2000), 2)
        qty        = random.randint(1, 10)
        discount   = round(random.choice([0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5]), 2)
        profit     = round(sales * random.uniform(-0.2, 0.45) * (1 - discount), 2)

        rows.append({
            "Row_ID":        i + 1,
            "Order_ID":      f"ORD-{year}-{random.randint(10000,99999)}",
            "Order_Date":    order_date,
            "Ship_Date":     ship_date,
            "Ship_Mode":     random.choice(SHIP_MODES),
            "Customer_ID":   customer,
            "Customer_Name": customer.replace("_", " "),
            "Segment":       segment,
            "Country":       "United States",
            "City":          city,
            "State":         state,
            "Postal_Code":   str(random.randint(10000, 99999)),
            "Region":        region,
            "Product_ID":    f"PROD-{sub_cat[:3].upper()}-{random.randint(1000,9999)}",
            "Category":      category,
            "Sub_Category":  sub_cat,
            "Product_Name":  f"{sub_cat} Model {random.randint(100,999)}",
            "Sales":         sales,
            "Quantity":      qty,
            "Discount":      discount,
            "Profit":        profit,
        })

    df = pd.DataFrame(rows)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Ship_Date"]  = pd.to_datetime(df["Ship_Date"])

    con = duckdb.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS orders")
    con.execute("CREATE TABLE orders AS SELECT * FROM df")
    count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    con.close()
    print(f"Generated {count:,} synthetic rows → {DB_PATH}")


if __name__ == "__main__":
    generate()
