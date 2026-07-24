# models/feature_importance.py
"""
Loads the trained fuel model and plots feature importances.

Run from the project root with:
    python models/feature_importance.py
"""

import os
import joblib
import matplotlib.pyplot as plt

FEATURES = ['speed', 'cargo_weight', 'beaufort_scale', 'dwt', 'built_year']
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fuel_model.pkl')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'feature_importance.png')

if __name__ == "__main__":
    model = joblib.load(MODEL_PATH)
    importances = model.feature_importances_

    # Sort features by importance, descending
    order = importances.argsort()[::-1]
    sorted_features = [FEATURES[i] for i in order]
    sorted_importances = importances[order]

    for feat, imp in zip(sorted_features, sorted_importances):
        print(f"{feat:20s} {imp:.4f}")

    plt.figure(figsize=(8, 5))
    plt.barh(sorted_features[::-1], sorted_importances[::-1], color="#2563eb")
    plt.xlabel("Feature Importance")
    plt.title("Fuel Consumption Model — Feature Importances (Random Forest)")
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150)
    print(f"\nChart saved to {OUTPUT_PATH}")