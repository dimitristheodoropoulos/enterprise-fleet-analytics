"""
Tests for the core FastAPI endpoints in main.py: health/home, fuel prediction,
and the deterministic + LLM-explained insurance risk scoring endpoint.
"""
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_predict_fuel_consumption_success(mock_fuel_model):
    payload = {
        "speed": 12.5,
        "cargo_weight": 60000,
        "beaufort_scale": 4,
        "dwt": 105000,
        "built_year": 2018,
    }
    response = client.post("/predict-fuel-consumption", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["predicted_fuel_consumption_tons_per_day"] == 12.34


def test_predict_fuel_consumption_model_not_loaded(monkeypatch):
    monkeypatch.setattr(main, "fuel_model", None)
    payload = {
        "speed": 12.5,
        "cargo_weight": 60000,
        "beaufort_scale": 4,
        "dwt": 105000,
        "built_year": 2018,
    }
    response = client.post("/predict-fuel-consumption", json=payload)
    assert response.status_code == 503


def test_predict_insurance_risk_low_risk(mock_llm_client):
    payload = {"speed_knots": 8.0, "beaufort_scale": 3, "built_year": 2022}
    response = client.post("/predict-insurance-risk", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "Low Risk"
    assert "-5%" in body["premium_adjustment"]
    assert body["business_reasoning"] == "Mocked LLM explanation in Greek."


def test_predict_insurance_risk_high_risk_deterministic_score(mock_llm_client):
    payload = {"speed_knots": 18.5, "beaufort_scale": 7, "built_year": 2005}
    response = client.post("/predict-insurance-risk", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "High Risk"
    assert body["risk_score"] == 79.3


def test_predict_insurance_risk_llm_failure_falls_back_gracefully(monkeypatch):
    """
    If the LLM call raises, business_reasoning must fall back to the deterministic
    hardcoded string -- never propagate the exception to the caller.
    """
    def raise_error(*args, **kwargs):
        raise RuntimeError("Simulated LLM outage")

    monkeypatch.setattr(main.client.chat.completions, "create", raise_error)

    payload = {"speed_knots": 18.5, "beaufort_scale": 7, "built_year": 2005}
    response = client.post("/predict-insurance-risk", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "High Risk"
    assert body["business_reasoning"] == "Εντοπίστηκε ριψοκίνδυνη συμπεριφορά. Αυξημένη πιθανότητα απαίτησης."


def test_get_vessels(mock_db_connection):
    mock_db_connection.fetchall.return_value = [
        {"vessel_id": 1, "vessel_name": "Test Vessel", "vessel_type": "Cargo"}
    ]
    response = client.get("/vessels")
    assert response.status_code == 200
    assert response.json()[0]["vessel_name"] == "Test Vessel"


def test_get_vessel_analytics_no_data(mock_db_connection):
    mock_db_connection.fetchone.return_value = {"total_telemetry_records": 0}
    response = client.get("/vessels/999/analytics")
    assert response.status_code == 200
    assert "error" in response.json()
