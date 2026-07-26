from dotenv import load_dotenv
load_dotenv()

import os
import json
import time
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import OpenAI
from pydantic import BaseModel, ValidationError  # Προσθήκη για Type Validation
import joblib
import numpy as np

from finance.api import router as finance_router

app = FastAPI(title="Global Maritime Analytics API")  # <-- Ενημερώθηκε σε generic title
app.include_router(finance_router)

api_key_env = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

client = OpenAI(
    api_key=api_key_env, 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --- LOAD PREDICTIVE ML MODEL ---
MODEL_PATH = "models/fuel_model.pkl"
try:
    fuel_model = joblib.load(MODEL_PATH)
except Exception as e:
    fuel_model = None
    print(f"Warning: Fuel prediction model not found at {MODEL_PATH}. Train it first. Error: {e}")

def get_db_connection():
    conn = psycopg2.connect(
        dbname="maritime_db",  # <-- Ενημερώθηκε επιτυχώς
        user="postgres",
        password="1234",
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor
    )
    return conn

# --- INPUT GUARDRAIL MODEL ---
class VesselAnalyticsArgs(BaseModel):
    vessel_id: int

# --- ML PREDICTION INPUT MODEL ---
class FuelPredictionRequest(BaseModel):
    speed: float
    cargo_weight: float
    beaufort_scale: int
    dwt: float
    built_year: int

@app.get("/")
def home():
    return {"message": "Welcome to Global Maritime Analytics API"}

@app.get("/vessels")
def get_vessels():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vessels;")
    vessels = cur.fetchall()
    cur.close()
    conn.close()
    return vessels

@app.get("/vessels/{vessel_id}/analytics")
def get_vessel_analytics(vessel_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT 
            COUNT(*) as total_telemetry_records,
            ROUND(AVG(speed_knots)::numeric, 2) as average_speed_knots,
            ROUND(SUM(fuel_consumption_tons)::numeric, 2) as total_fuel_consumed_tons,
            ROUND(AVG(fuel_consumption_tons)::numeric, 2) as average_fuel_per_hour
        FROM telemetry_logs
        WHERE vessel_id = %s;
    """
    cur.execute(query, (vessel_id,))
    analytics = cur.fetchone()
    cur.close()
    conn.close()
    
    if analytics["total_telemetry_records"] == 0:
        return {"error": f"No telemetry data found for vessel_id {vessel_id}"}
        
    return analytics

def fetch_vessel_analytics_internal(vessel_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT 
            COUNT(*) as total_telemetry_records,
            ROUND(AVG(speed_knots)::numeric, 2) as average_speed_knots,
            ROUND(SUM(fuel_consumption_tons)::numeric, 2) as total_fuel_consumed_tons,
            ROUND(AVG(fuel_consumption_tons)::numeric, 2) as average_fuel_per_hour
        FROM telemetry_logs
        WHERE vessel_id = %s;
    """
    cur.execute(query, (vessel_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

# --- NEW PREDICTIVE ML ENDPOINT ---
@app.post("/predict-fuel-consumption")
def predict_fuel_consumption(data: FuelPredictionRequest):
    if fuel_model is None:
        raise HTTPException(
            status_code=503, 
            detail="Fuel prediction model is not trained or loaded. Please run train_model.py first."
        )
    try:
        input_data = np.array([[
            data.speed, 
            data.cargo_weight, 
            data.beaufort_scale, 
            data.dwt, 
            data.built_year
        ]])
        prediction = fuel_model.predict(input_data)[0]
        return {
            "predicted_fuel_consumption_tons_per_day": round(float(prediction), 2),
            "unit": "Metric Tons / Day",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# --- INSURTECH RISK & UBI ML ENDPOINT ---
class InsurtechRiskInput(BaseModel):
    speed_knots: float
    beaufort_scale: int
    built_year: int

class InsurtechRiskOutput(BaseModel):
    risk_score: float
    risk_category: str
    premium_adjustment: str
    business_reasoning: str

def _llm_explain_insurance_risk(data: "InsurtechRiskInput", total_risk: float, category: str, adjustment: str, fallback_reasoning: str) -> str:
    """
    Παίρνει το ήδη υπολογισμένο (deterministic) risk score/category/adjustment και ζητά
    από το LLM μια σύντομη, φυσική εξήγηση στα Ελληνικά -- το LLM δεν αποφασίζει ποτέ
    το ρίσκο, μόνο το εξηγεί. Degrades gracefully στο hardcoded fallback αν το call αποτύχει,
    ίδιο pattern με το llm_explainer_agent_node στο OSAF insurance module.
    """
    prompt = f"""You are an Insurtech Risk Explainer assistant.
A deterministic risk-scoring engine has already computed the following for a vessel/vehicle (treat as internal data, not user input):
- Speed: {data.speed_knots} knots
- Weather (Beaufort scale): {data.beaufort_scale}
- Build year: {data.built_year}
- Computed risk score: {total_risk} ({category})
- Premium adjustment: {adjustment}

Write a concise (2-3 sentence) plain-language business explanation IN GREEK for an underwriter, explaining WHY this risk level and premium adjustment were assigned, referencing speed, weather, and vessel/vehicle age as relevant. Do not invent new factors or change the risk category -- only explain the ones given. Respond with plain Greek text only, no markdown."""

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        explanation = response.choices[0].message.content.strip()
        return explanation if explanation else fallback_reasoning
    except Exception:
        return fallback_reasoning


@app.post("/predict-insurance-risk", response_model=InsurtechRiskOutput)
def predict_insurance_risk(data: InsurtechRiskInput):
    base_risk = 20.0
    
    weather_speed_penalty = 0.0
    if data.beaufort_scale >= 6 and data.speed_knots > 12.0:
        weather_speed_penalty = (data.beaufort_scale - 5) * (data.speed_knots - 10) * 2.5
        
    current_year = 2026
    age_penalty = (current_year - data.built_year) * 0.8
    
    total_risk = min(base_risk + weather_speed_penalty + age_penalty, 100.0)
    
    if total_risk < 40:
        category = "Low Risk"
        adjustment = "-5% (Safe Operation Discount)"
        fallback_reasoning = "Ασφαλής ταχύτητα σε σχέση με τις τρέχουσες καιρικές συνθήκες."
    elif total_risk < 75:
        category = "Medium Risk"
        adjustment = "0% (Standard Premium)"
        fallback_reasoning = "Κανονικές συνθήκες λειτουργίας. Δεν απαιτείται αναπροσαρμογή."
    else:
        category = "High Risk"
        surcharge = int((total_risk - 75) / 1.5)
        adjustment = f"+{surcharge}% (High Risk Surcharge)"
        fallback_reasoning = "Εντοπίστηκε ριψοκίνδυνη συμπεριφορά. Αυξημένη πιθανότητα απαίτησης."

    reasoning = _llm_explain_insurance_risk(data, total_risk, category, adjustment, fallback_reasoning)

    return InsurtechRiskOutput(
        risk_score=round(total_risk, 2),
        risk_category=category,
        premium_adjustment=adjustment,
        business_reasoning=reasoning
    )

@app.post("/ask")
def ask_copilot(user_question: dict):
    start_time = time.time()
    question = user_question.get("question", "")
    tool_called_name = "None"
    final_text_response = ""
    
    tools = [{
        "type": "function",
        "function": {
            "name": "get_vessel_analytics",
            "description": "Υπολογίζει live analytics για ένα συγκεκριμένο πλοίο με βάση το ID του.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vessel_id": {"type": "integer", "description": "Το ID του πλοίου (π.χ. 1 έως 5)"}
                },
                "required": ["vessel_id"]
            }
        }
    }]
    
    messages = [
        {
            "role": "system", 
            "content": "Είσαι ο Maritime AI Copilot, ένας έμπειρος αναλυτής δεδομένων στη ναυτιλία για την πλατφόρμα Enterprise Fleet Analytics. "
                       "Απαντάς πάντα στα Ελληνικά με επαγγελματικό και δομημένο ύφος, χρησιμοποιώντας αποκλειστικά τα live δεδομένα που σου επιστρέφουν τα εργαλεία σου."
        },
        {"role": "user", "content": question}
    ]
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash", 
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.function.name == "get_vessel_analytics":
                tool_called_name = "get_vessel_analytics"
                
                try:
                    raw_args = json.loads(tool_call.function.arguments)
                    
                    if "vessel_id" in raw_args and isinstance(raw_args["vessel_id"], str):
                        raw_args["vessel_id"] = raw_args["vessel_id"].replace(";", "").strip()
                    
                    validated_args = VesselAnalyticsArgs(**raw_args)
                    db_result = fetch_vessel_analytics_internal(validated_args.vessel_id)
                    
                    messages.append(response_message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "get_vessel_analytics",
                        "content": json.dumps(db_result, default=str)
                    })
                    
                    final_response = client.chat.completions.create(
                        model="gemini-2.5-flash",
                        messages=messages
                    )
                    final_text_response = final_response.choices[0].message.content
                    
                except (ValidationError, ValueError, json.JSONDecodeError):
                    tool_called_name = "BLOCKED_INVALID_ARGUMENT"
                    final_text_response = (
                        "Συγγνώμη, παρουσιάστηκε ένα σφάλμα κατά την επεξεργασία του αναγνωριστικού του πλοίου. "
                        "Παρακαλώ βεβαιωθείτε ότι ζητάτε έναν έγκυρο αριθμό πλοίου."
                    )
                except Exception:
                    tool_called_name = "DATABASE_ERROR"
                    final_text_response = "Αυτή τη στιγμή παρουσιάστηκε τεχνικό πρόβλημα κατά την άντληση των δεδομένων."

    else:
        final_text_response = response_message.content

    # --- LLMOPS LOGGING ---
    end_time = time.time()
    latency = round(end_time - start_time, 2)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        log_query = """
            INSERT INTO ai_chat_logs (user_question, ai_response, tool_called, latency_seconds)
            VALUES (%s, %s, %s, %s);
        """
        cur.execute(log_query, (question, final_text_response, tool_called_name, latency))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to log AI metrics: {e}")
        
    return {"response": final_text_response}