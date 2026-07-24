# models/speed_optimizer.py
"""
Recommends the optimal cruising speed for a voyage, given a distance
and a time budget, using the trained fuel consumption model to
evaluate the total fuel cost of each candidate speed.

Run from the project root with:
    python models/speed_optimizer.py
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fuel_model.pkl')
CHART_PATH = os.path.join(os.path.dirname(__file__), 'speed_optimization.png')

FEATURES = ['speed', 'cargo_weight', 'beaufort_scale', 'dwt', 'built_year']


def optimize_speed(distance_nm, cargo_weight, beaufort_scale, dwt, built_year,
                    max_hours=None, min_speed=8.0, max_speed=16.0, step=0.25):
    """
    Evaluates a range of candidate speeds and returns:
      - a DataFrame with speed, travel time, and total fuel for each candidate
      - the recommended (fuel-minimizing) speed that meets the time budget, if any
    """
    model = joblib.load(MODEL_PATH)

    candidate_speeds = np.arange(min_speed, max_speed + step, step)
    rows = []
    for speed in candidate_speeds:
        input_data = pd.DataFrame([[speed, cargo_weight, beaufort_scale, dwt, built_year]],
                                   columns=FEATURES)
        fuel_rate = model.predict(input_data)[0]  # tons/day
        travel_hours = distance_nm / speed
        travel_days = travel_hours / 24
        total_fuel = fuel_rate * travel_days
        rows.append({
            "speed": round(speed, 2),
            "travel_hours": round(travel_hours, 2),
            "fuel_rate_tons_per_day": round(fuel_rate, 2),
            "total_fuel_tons": round(total_fuel, 2),
        })

    results = pd.DataFrame(rows)

    feasible = results if max_hours is None else results[results["travel_hours"] <= max_hours]

    if feasible.empty:
        print(f"No candidate speed can meet the {max_hours}h time budget "
              f"within the {min_speed}-{max_speed} knot search range.")
        best = None
    else:
        best = feasible.loc[feasible["total_fuel_tons"].idxmin()]

    return results, best


def plot_tradeoff(results, best, max_hours=None):
    fig, ax1 = plt.subplots(figsize=(8, 6))

    ax1.plot(results["speed"], results["total_fuel_tons"], color="#2563eb", label="Total Fuel (tons)")
    ax1.set_xlabel("Speed (knots)")
    ax1.set_ylabel("Total Fuel for Voyage (tons)", color="#2563eb")
    ax1.tick_params(axis='y', labelcolor="#2563eb")

    ax2 = ax1.twinx()
    ax2.plot(results["speed"], results["travel_hours"], color="#ef4444", linestyle="--", label="Travel Time (hours)")
    ax2.set_ylabel("Travel Time (hours)", color="#ef4444")
    ax2.tick_params(axis='y', labelcolor="#ef4444")

    if max_hours is not None:
        ax2.axhline(y=max_hours, color="#ef4444", linestyle=":", alpha=0.5)

    if best is not None:
        ax1.scatter([best["speed"]], [best["total_fuel_tons"]], color="#22c55e", s=100,
                    zorder=5, label="Recommended Speed")

    plt.title("Speed vs. Fuel Cost / Travel Time Trade-off")
    fig.tight_layout()
    plt.savefig(CHART_PATH, dpi=150)
    print(f"Chart saved to {CHART_PATH}")


if __name__ == "__main__":
    # Example scenario: 1,000 nautical mile voyage, moderate weather,
    # must arrive within 90 hours (3.75 days)
    DISTANCE_NM = 1000
    CARGO_WEIGHT = 60000
    BEAUFORT_SCALE = 4
    DWT = 105000
    BUILT_YEAR = 2018
    MAX_HOURS = 90

    results, best = optimize_speed(
        distance_nm=DISTANCE_NM,
        cargo_weight=CARGO_WEIGHT,
        beaufort_scale=BEAUFORT_SCALE,
        dwt=DWT,
        built_year=BUILT_YEAR,
        max_hours=MAX_HOURS,
    )

    print(f"\nScenario: {DISTANCE_NM} nm voyage, must arrive within {MAX_HOURS}h\n")
    print(results.to_string(index=False))

    if best is not None:
        print(f"\nRecommended speed: {best['speed']} knots")
        print(f"  -> Travel time: {best['travel_hours']}h")
        print(f"  -> Total fuel: {best['total_fuel_tons']} tons")

    plot_tradeoff(results, best, max_hours=MAX_HOURS)