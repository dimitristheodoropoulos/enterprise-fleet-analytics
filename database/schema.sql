import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 1. Σύνδεση με την τοπική PostgreSQL (Docker Container)
try:
    conn = psycopg2.connect(
        dbname="maritime_db",  # <-- Αλλάχθηκε σε generic
        user="postgres",
        password="1234", 
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    print("-> Successfully connected to local PostgreSQL database.")
except Exception as e:
    print(f"-> Connection Error: {e}")
    exit()

# 2. Εισαγωγή του Mock Fleet (Generic Maritime Fleet)
vessels_data = [
    ("Poseidon E.", "Tanker", 105000, 2018),   # Ευθυγραμμισμένο με τα live δεδομένα σου
    ("Alpha Bulker", "Dry Bulk", 82000, 2020), # Ευθυγραμμισμένο με τα live δεδομένα σου
    ("Ocean Rider", "Tanker", 115000, 2015),   # Ευθυγραμμισμένο με τα live δεδομένα σου
    ("Aegean Titan", "Tanker", 310000, 2022),
    ("Thassos Wave", "Dry Bulk", 64000, 2013)
]

vessel_ids = []
for v in vessels_data:
    cursor.execute(
        "INSERT INTO vessels (vessel_name, vessel_type, capacity_dwt, year_built) VALUES (%s, %s, %s, %s) RETURNING vessel_id;",
        v
    )
    vessel_id = cursor.fetchone()[0]
    vessel_ids.append(vessel_id)

conn.commit()
print(f"-> Successfully inserted {len(vessels_data)} generic vessels into the database.")

# 3. Παραγωγή Συνθετικών Δεδομένων Τηλεμετρίας (Telemetry Mock Data)
num_records = 1500
start_date = datetime(2026, 5, 1)

vids = np.random.choice(vessel_ids, size=num_records)
dates = [start_date + timedelta(days=int(np.random.randint(0, 60))) for _ in range(num_records)]
wind = np.random.randint(1, 9, size=num_records) # Beaufort scale 1-8

# Προσομοίωση Φυσικής: Η ταχύτητα μειώνεται όταν ο καιρός (wind) χειροτερεύει
base_speed = np.random.uniform(11.0, 15.0, size=num_records)
speed = base_speed - (wind * 0.3)

# Προσομοίωση Φυσικής: Η κατανάλωση καυσίμου αυξάνεται εκθετικά με την ταχύτητα και τον κόντρα καιρό
fuel = (speed ** 1.7) * 0.16 + (wind * 0.85)

cargo = np.random.randint(25000, 90000, size=num_records)
status = [random.choice(['In Transit', 'In Transit', 'In Transit', 'In Port']) for _ in range(num_records)]

# Μηδενισμός ταχύτητας και κατανάλωσης αν το πλοίο είναι στο λιμάνι (In Port)
for i in range(num_records):
    if status[i] == 'In Port':
        speed[i] = 0.0
        fuel[i] = np.random.uniform(1.5, 3.0) # Μόνο η γεννήτρια του λιμανιού καίει

# Δημιουργία του Dataframe
df = pd.DataFrame({
    'vessel_id': vids,
    'log_date': dates,
    'speed_knots': np.round(speed, 2),
    'fuel_consumption_tons': np.round(fuel, 2),
    'wind_beaufort': wind,
    'cargo_weight_tons': cargo,
    'route_status': status
})

# 4. Bulk Insert των Telemetry Logs στη PostgreSQL
print("-> Inserting telemetry records into database...")
for index, row in df.iterrows():
    cursor.execute(
        """
        INSERT INTO telemetry_logs (vessel_id, log_date, speed_knots, fuel_consumption_tons, wind_beaufort, cargo_weight_tons, route_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """,
        (int(row['vessel_id']), row['log_date'], float(row['speed_knots']), float(row['fuel_consumption_tons']), int(row['wind_beaufort']), int(row['cargo_weight_tons']), row['route_status'])
    )

conn.commit()
cursor.close()
conn.close()
print("-> Data generation and database population completed successfully!")