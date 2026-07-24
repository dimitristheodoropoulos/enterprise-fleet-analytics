# models/forecast_fuel_trend.py
"""
Forecasts fleet-wide daily fuel consumption using time-series methods,
with a proper time-ordered train/test split (not random shuffling).

Run from the project root with:
    python models/forecast_fuel_trend.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing

MODEL_DIR = os.path.dirname(__file__)
CHART_PATH = os.path.join(MODEL_DIR, 'fuel_forecast.png')

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "maritime_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "1234"),
}

QUERY = """
    SELECT
        log_date::date AS day,
        SUM(fuel_consumption_tons) AS total_fuel
    FROM telemetry_logs
    WHERE route_status = 'In Transit'
    GROUP BY log_date::date
    ORDER BY day;
"""


def load_daily_series() -> pd.Series:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        df = pd.read_sql(QUERY, conn)
    finally:
        conn.close()
    df['day'] = pd.to_datetime(df['day'])
    series = df.set_index('day')['total_fuel'].asfreq('D').interpolate()
    print(f"Loaded {len(series)} daily observations, from {series.index.min().date()} to {series.index.max().date()}")
    return series


if __name__ == "__main__":
    series = load_daily_series()

    # Time-ordered split: last 14 days held out for testing (never shuffle time series data)
    TEST_DAYS = 14
    train = series.iloc[:-TEST_DAYS]
    test = series.iloc[-TEST_DAYS:]

    model = ExponentialSmoothing(
        train, trend='add', seasonal='add', seasonal_periods=7  # weekly seasonality
    ).fit()

    forecast = model.forecast(TEST_DAYS)

    mae = mean_absolute_error(test, forecast)
    rmse = np.sqrt(mean_squared_error(test, forecast))
    print(f"\nForecast evaluation on last {TEST_DAYS} held-out days:")
    print(f"MAE:  {mae:.2f} tons/day")
    print(f"RMSE: {rmse:.2f} tons/day")
    print(f"Naive baseline (yesterday's value) MAE: {mean_absolute_error(test, train.iloc[-1:].repeat(TEST_DAYS).values):.2f} tons/day")

    plt.figure(figsize=(10, 6))
    plt.plot(train.index[-30:], train.values[-30:], label="Training data", color="#2563eb")
    plt.plot(test.index, test.values, label="Actual (held out)", color="#22c55e", marker='o')
    plt.plot(test.index, forecast.values, label="Forecast", color="#ef4444", linestyle="--", marker='x')
    plt.xlabel("Date")
    plt.ylabel("Total Fleet Fuel Consumption (tons/day)")
    plt.title("Fleet-wide Daily Fuel Consumption Forecast (Holt-Winters)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=150)
    print(f"Chart saved to {CHART_PATH}")