import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Δημιουργία φακέλου αν δεν υπάρχει
os.makedirs('excel_showcase', exist_ok=True)

np.random.seed(42)
n_rows = 5000

vessel_types = ['Container', 'Bulk Carrier', 'Tanker', 'LNG Carrier']
vessels = [f"MV Fleet_{i:02d}" for i in range(1, 21)]

start_time = datetime.now() - timedelta(days=60)

data = {
    'telemetry_id': [f"TEL-{10000 + i}" for i in range(n_rows)],
    'vessel_name': np.random.choice(vessels, n_rows),
    'vessel_type': np.random.choice(vessel_types, n_rows),
    'speed_knots': np.round(np.random.uniform(8.0, 24.0, n_rows), 2),
    'beaufort_scale': np.random.randint(1, 10, n_rows),
    'cargo_weight_tons': np.random.randint(5000, 50000, n_rows),
    'route_status': np.random.choice(['Underway', 'Anchored', 'Moored'], n_rows, p=[0.75, 0.15, 0.10]),
    'timestamp': [start_time + timedelta(minutes=15 * i) for i in range(n_rows)]
}

df = pd.DataFrame(data)

# Υπολογισμός κατανάλωσης καυσίμου βάσει ταχύτητας και μποφόρ
df['fuel_consumption_mt'] = np.round(
    (df['speed_knots'] ** 1.7) * 0.04 + (df['beaufort_scale'] * 1.5) + np.random.normal(0, 1.5, n_rows),
    2
)
df['fuel_consumption_mt'] = df['fuel_consumption_mt'].clip(lower=0.5)

# Εισαγωγή 1% κενών τιμών στα μποφόρ (για επίδειξη Data Cleaning στο Excel)
df.loc[df.sample(frac=0.01, random_state=42).index, 'beaufort_scale'] = np.nan

output_path = 'excel_showcase/fleet_telemetry_sample.csv'
df.to_csv(output_path, index=False)
print(f"✅ Δημιουργήθηκαν με επιτυχία {n_rows} εγγραφές στο: {output_path}")