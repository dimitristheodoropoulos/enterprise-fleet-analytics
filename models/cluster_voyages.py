# models/cluster_voyages.py
"""
Clusters individual telemetry records into voyage efficiency profiles
using K-Means, based on speed, fuel consumption, weather, and cargo load.

Run from the project root with:
    python models/cluster_voyages.py
"""

import os
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from run_training import load_data

FEATURES = ['speed', 'fuel_consumption', 'beaufort_scale', 'cargo_weight']
N_CLUSTERS = 3

MODEL_DIR = os.path.dirname(__file__)
KMEANS_PATH = os.path.join(MODEL_DIR, 'voyage_clusters.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'voyage_scaler.pkl')
CHART_PATH = os.path.join(MODEL_DIR, 'voyage_clusters.png')


def label_clusters(df, cluster_col='cluster'):
    """Assigns human-readable labels based on mean fuel-per-knot per cluster."""
    fuel_per_speed = df.groupby(cluster_col).apply(
        lambda g: (g['fuel_consumption'] / g['speed'].replace(0, np.nan)).mean()
    )
    ordered = fuel_per_speed.sort_values().index.tolist()
    labels = {ordered[0]: "Efficient", ordered[1]: "Moderate", ordered[2]: "Inefficient"}
    return labels


if __name__ == "__main__":
    df = load_data()

    # Exclude in-port records (speed=0) — clustering is meant for underway voyages
    df = df[df['speed'] > 0].reset_index(drop=True)

    X = df[FEATURES]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    sil_score = silhouette_score(X_scaled, df['cluster'])
    print(f"Silhouette Score: {sil_score:.4f}\n")

    labels = label_clusters(df)
    df['profile'] = df['cluster'].map(labels)

    print("Cluster summary:")
    summary = df.groupby('profile')[FEATURES].mean().round(2)
    summary['count'] = df['profile'].value_counts()
    print(summary)

    # Save model + scaler for reuse
    joblib.dump(kmeans, KMEANS_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"\nSaved cluster model to {KMEANS_PATH}")

    # Scatter plot: speed vs fuel consumption, colored by profile
    plt.figure(figsize=(8, 6))
    colors = {"Efficient": "#22c55e", "Moderate": "#f59e0b", "Inefficient": "#ef4444"}
    for profile, color in colors.items():
        subset = df[df['profile'] == profile]
        plt.scatter(subset['speed'], subset['fuel_consumption'],
                    label=profile, color=color, alpha=0.4, s=10)
    plt.xlabel("Speed (knots)")
    plt.ylabel("Fuel Consumption (tons/day)")
    plt.title("Voyage Efficiency Clusters (K-Means)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=150)
    print(f"Chart saved to {CHART_PATH}")