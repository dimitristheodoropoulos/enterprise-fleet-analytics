import os
import json
import time
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import OpenAI
from pydantic import BaseModel, ValidationError  # Προσθήκη για Type Validation

app = FastAPI(title="Global Maritime Analytics API")  # <-- Ενημερώθηκε σε generic title

api_key_env = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

client = OpenAI(
    api_key=api_key_env, 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

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
                    
                except (ValidationError, ValueError, json.JSONDecodeError) as e:
                    tool_called_name = "BLOCKED_INVALID_ARGUMENT"
                    final_text_response = (
                        "Συγγνώμη, παρουσιάστηκε ένα σφάλμα κατά την επεξεργασία του αναγνωριστικού του πλοίου. "
                        "Παρακαλώ βεβαιωθείτε ότι ζητάτε έναν έγκυρο αριθμό πλοίου."
                    )
                except Exception as e:
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