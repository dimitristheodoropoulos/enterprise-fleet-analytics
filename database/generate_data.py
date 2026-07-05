import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 1. Σύνδεση με την PostgreSQL στο Docker
try:
    conn = psycopg2.connect(
        dbname="maritime_db",
        user="postgres",
        password="1234", 
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    print("-> Successfully connected to maritime_db.")
except Exception as e:
    print(f"-> Connection Error: {e}")
    exit()

# Καθαρισμός παλιών δεδομένων για να μην έχουμε διπλοεγγραφές
print("-> Cleaning up old records...")
cursor.execute("TRUNCATE telemetry_logs RESTART IDENTITY CASCADE;")
cursor.execute("TRUNCATE vessels RESTART IDENTITY CASCADE;")
conn.commit()

# 2. Εισαγωγή των 5 Generic Πλοίων
vessels_data = [
    ("Poseidon E.", "Tanker", 105000, 2018),
    ("Alpha Bulker", "Dry Bulk", 82000, 2020),
    ("Ocean Rider", "Tanker", 115000, 2015),
    ("Aegean Titan", "Tanker", 310000, 2022),
    ("Thassos Wave", "Dry Bulk", 64000, 2013)
]

vessel_ids = []
for v in vessels_data:
    cursor.execute(
        "INSERT INTO vessels (vessel_name, vessel_type, capacity_dwt, year_built) VALUES (%s, %s, %s, %s) RETURNING vessel_id;",
        v
    )
    vessel_ids.append(cursor.fetchone()[0])

conn.commit()
print(f"-> Successfully inserted {len(vessel_ids)} generic vessels.")

# 3. Παραγωγή 100.000 Ιστορικών Εγγραφών Τηλεμετρίας (Vectorized Simulation)
num_records = 100000
start_date = datetime(2024, 1, 1) # Ξεκινάμε από το 2024 για να έχουμε πλούσιο ιστορικό στο Power BI

print("-> Generating 100,000 synthetic runtime logs...")

# Τυχαία κατανομή σε βάθος 2 ετών
dates = [start_date + timedelta(days=random.randint(0, 900)) for _ in range(num_records)]
vids = [random.choice(vessel_ids) for _ in range(num_records)]
wind = np.random.randint(1, 9, size=num_records) # Beaufort 1-8

# Προσομοίωση Φυσικής
base_speed = np.random.uniform(11.0, 15.0, size=num_records)
speed = base_speed - (wind * 0.3)
fuel = (speed ** 1.7) * 0.16 + (wind * 0.85)
cargo = np.random.randint(25000, 90000, size=num_records)
status = [random.choice(['In Transit', 'In Transit', 'In Transit', 'In Port']) for _ in range(num_records)]

for i in range(num_records):
    if status[i] == 'In Port':
        speed[i] = 0.0
        fuel[i] = np.random.uniform(1.5, 3.0)

df = pd.DataFrame({
    'vessel_id': vids,
    'log_date': dates,
    'speed_knots': np.round(speed, 2),
    'fuel_consumption_tons': np.round(fuel, 2),
    'wind_beaufort': wind,
    'cargo_weight_tons': cargo,
    'route_status': status
})

# 4. Ταχύτατο Bulk Insert
records = list(df.itertuples(index=False, name=None))
insert_query = """
    INSERT INTO telemetry_logs (vessel_id, log_date, speed_knots, fuel_consumption_tons, wind_beaufort, cargo_weight_tons, route_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

print("-> Injecting 100,000 logs into PostgreSQL...")
cursor.executemany(insert_query, records)
conn.commit()

cursor.close()
conn.close()
print("-> Done! Database is fully populated with production-scale data.")