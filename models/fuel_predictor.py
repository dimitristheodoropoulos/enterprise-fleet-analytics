# models/fuel_predictor.py
import os
import joblib
import numpy as np

_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fuel_model.pkl')

class FuelPredictor:
    """Loads the trained fuel consumption model once and serves predictions."""

    def __init__(self, model_path: str = _MODEL_PATH):
        self.model = joblib.load(model_path)

    def predict(self, speed: float, cargo_weight: float, beaufort_scale: int,
                dwt: float, built_year: int) -> float:
        input_data = np.array([[speed, cargo_weight, beaufort_scale, dwt, built_year]])
        prediction = self.model.predict(input_data)[0]
        return round(float(prediction), 2)


# Simple manual test when running this file directly:
#   python fuel_predictor.py
if __name__ == "__main__":
    predictor = FuelPredictor()
    result = predictor.predict(speed=12.5, cargo_weight=60000, beaufort_scale=4,
                                dwt=105000, built_year=2018)
    print(f"Predicted fuel consumption: {result} MT/day")