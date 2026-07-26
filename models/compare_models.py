# models/compare_models.py
"""
Compares multiple regression algorithms on the same fuel consumption
dataset, to demonstrate model selection methodology.

Run from the project root with:
    python models/compare_models.py
"""

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

from run_training import load_data  # reuses the same DB loading logic

FEATURES = ['speed', 'cargo_weight', 'beaufort_scale', 'dwt', 'built_year']
TARGET = 'fuel_consumption'


def evaluate_model(name, model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"{name:25s} | R2 = {r2:.4f} | RMSE = {rmse:.4f}")
    return {"model": name, "r2": r2, "rmse": rmse}


if __name__ == "__main__":
    df = load_data()
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    }

    print("\nModel comparison — fuel consumption prediction\n" + "-" * 55)
    results = [evaluate_model(name, model, X_train, X_test, y_train, y_test)
               for name, model in models.items()]

    best = max(results, key=lambda r: r["r2"])
    print("-" * 55)
    print(f"Best model: {best['model']} (R2 = {best['r2']:.4f})")