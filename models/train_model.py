# models/train_model.py
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

def train_fuel_model(df):
    # Feature Selection & Preprocessing
    features = ['speed', 'cargo_weight', 'beaufort_scale', 'dwt', 'built_year']
    target = 'fuel_consumption'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation metrics
    y_pred = model.predict(X_test)
    print(f"R2 Score: {r2_score(y_test, y_pred):.4f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
    
    # Save model (path is relative to this file's location, not the current working directory)
    model_path = os.path.join(os.path.dirname(__file__), 'fuel_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    return model