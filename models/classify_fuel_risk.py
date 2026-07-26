# models/classify_fuel_risk.py
"""
Reframes fuel consumption as a classification problem: predicts a
Low/Medium/High fuel-cost category for a voyage instead of an exact
tons/day value, using the same underlying features.

Run from the project root with:
    python models/classify_fuel_risk.py
"""

import os
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

from run_training import load_data

FEATURES = ['speed', 'cargo_weight', 'beaufort_scale', 'dwt', 'built_year']
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, 'fuel_risk_classifier.pkl')
CHART_PATH = os.path.join(MODEL_DIR, 'confusion_matrix.png')


def make_labels(df):
    """Buckets fuel_consumption into Low/Medium/High using terciles (33rd/66th percentile)."""
    low_cut, high_cut = df['fuel_consumption'].quantile([0.33, 0.66])
    conditions = [
        df['fuel_consumption'] <= low_cut,
        df['fuel_consumption'] <= high_cut,
    ]
    choices = ['Low', 'Medium']
    df['fuel_risk'] = np.select(conditions, choices, default='High')
    print(f"Category thresholds — Low: <= {low_cut:.2f}, Medium: <= {high_cut:.2f}, High: > {high_cut:.2f} tons/day")
    return df


if __name__ == "__main__":
    df = load_data()
    df = make_labels(df)

    X = df[FEATURES]
    y = df['fuel_risk']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    labels = ['Low', 'Medium', 'High']
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap='Blues', values_format='d')
    plt.title("Fuel Cost Risk Classification — Confusion Matrix")
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=150)
    print(f"Confusion matrix saved to {CHART_PATH}")