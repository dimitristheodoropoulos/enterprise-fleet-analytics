# models/run_training.py
"""
Entry point script: loads telemetry data from PostgreSQL,
prepares it, and trains the fuel consumption prediction model.

Run from the project root with:
    python models/run_training.py
"""

import os
import pandas as pd
import psycopg2
from train_model import train_fuel_model

# --- Database connection settings ---
# Adjust these to match how database/generate_data.py connects,
# or set them as environment variables before running.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "maritime_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "1234"),
}

QUERY = """
    SELECT
        t.speed_knots AS speed,
        t.cargo_weight_tons AS cargo_weight,
        t.wind_beaufort AS beaufort_scale,
        v.capacity_dwt AS dwt,
        v.year_built AS built_year,
        t.fuel_consumption_tons AS fuel_consumption
    FROM telemetry_logs t
    JOIN vessels v ON t.vessel_id = v.vessel_id
    WHERE t.fuel_consumption_tons IS NOT NULL;
"""

def load_data() -> pd.DataFrame:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        df = pd.read_sql(QUERY, conn)
    finally:
        conn.close()
    print(f"Loaded {len(df)} rows for training.")
    return df

if __name__ == "__main__":
    df = load_data()
    train_fuel_model(df)