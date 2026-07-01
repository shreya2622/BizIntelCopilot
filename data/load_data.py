"""
Phase 1: Load Superstore CSV into DuckDB.

Usage:
    python data/load_data.py --csv path/to/superstore.csv

The script creates/replaces superstore.db in the project root and
creates an `orders` table from the CSV.
"""

import argparse
import os
import duckdb
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "superstore.db")


def load(csv_path: str) -> None:
    df = pd.read_csv(csv_path, encoding="latin-1")

    # Normalise column names: strip spaces, replace spaces with underscores
    df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]

    # Parse dates
    for col in ("Order_Date", "Ship_Date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=False, errors="coerce")

    con = duckdb.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS orders")
    con.execute("CREATE TABLE orders AS SELECT * FROM df")
    row_count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    con.close()

    print(f"Loaded {row_count:,} rows into {DB_PATH}")
    print("Columns:", list(df.columns))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to Superstore CSV file")
    args = parser.parse_args()
    load(args.csv)
