import os
import sys
import json
import re
import psycopg2
from google import genai
from google.genai import types

# Εξασφάλιση σωστού encoding για ελληνικά και emojis στα Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 1. Αρχικοποίηση του Gemini Client με το νέο επίσημο SDK
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_FALLBACK_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# 2. Παράμετροι Σύνδεσης με τη Βάση Δεδομένων (PostgreSQL Container)
DB_CONFIG = {
    "host": "localhost",
    "database": "maritime_db",  # <-- Ενημερώθηκε επιτυχώς
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def validate_and_verify_sql(generated_sql: str, db_connection) -> tuple[bool, str]:
    """
    PRODUCTION GUARDRAIL: Approaches AI output with healthy skepticism 
    by verifying the generated SQL syntax and safety before execution.
    """
    # Καθαρισμός markdown μορφοποίησης αν υπάρχει
    clean_sql = generated_sql.strip()
    if clean_sql.startswith("```sql"):
        clean_sql = clean_sql.split("```sql")[1].split("```")[0].strip()
    elif clean_sql.startswith("```"):
        clean_sql = clean_sql.split("```")[1].split("```")[0].strip()
        
    # 1. Ασφάλεια: Μπλοκάρισμα καταστροφικών ενεργειών (DML/DDL)
    forbidden_keywords = [r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b", r"\bUPDATE\b", r"\bALTER\b", r"\bTRUNCATE\b"]
    for keyword in forbidden_keywords:
        if re.search(keyword, clean_sql, re.IGNORECASE):
            return False, f"⚠️ Ακύρωση: Ανιχνεύθηκε μη ασφαλής ενέργεια ({keyword}). Το query μπλοκαρίστηκε."
            
    # 2. Επαλήθευση (Verification): Έλεγχος συντακτικού μέσω EXPLAIN
    try:
        with db_connection.cursor() as cursor:
            # Το EXPLAIN αναλύει το πλάνο εκτέλεσης στην PostgreSQL χωρίς να τρέξει ή να δεσμεύσει πόρους
            cursor.execute(f"EXPLAIN {clean_sql}")
            return True, clean_sql
    except psycopg2.Error as e:
        db_connection.rollback()
        return False, f"⚠️ Ακύρωση: Το LLM παρήγαγε μη έγκυρη SQL. Σφάλμα Βάσης: {e.pgerror.strip()}"

def generate_embedding(text):
    """Παράγει vector embedding χρησιμοποιώντας το σωστό μοντέλο γενιάς 2 του SDK"""
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    )
    return response.embeddings[0].values

def text_to_sql_agent(user_query):
    """
    AI Agent που μετατρέπει φυσική γλώσσα σε SQL, εκτελεί το query στη βάση της Enterprise Fleet Analytics,
    παράγει business ανάλυση στα Ελληνικά και αποθηκεύει logs με Vector Embeddings.
    """
    db_schema_prompt = """
    You are an expert Data Analyst for an Enterprise Fleet Analytics system. Given the following PostgreSQL database schema, 
    generate a valid SQL query that answers the user's request. Return ONLY the raw SQL query, no markdown, no code blocks.
    
    Tables:
    1. table: vessels
       columns: vessel_id (SERIAL PRIMARY KEY), vessel_name (VARCHAR), vessel_type (VARCHAR), capacity_dwt (INT), year_built (INT)
    
    2. table: telemetry_logs
       columns: log_id (SERIAL PRIMARY KEY), vessel_id (INT REFERENCES vessels), log_date (DATE), speed_knots (NUMERIC), fuel_consumption_tons (NUMERIC), wind_beaufort (INT), cargo_weight_tons (INT), route_status (VARCHAR)
    
    Note: The month 'June' corresponds to EXTRACT(MONTH FROM log_date) = 6 or log_date BETWEEN '2026-06-01' AND '2026-06-30'.
    """

    conn = None
    try:
        # Step A: Παραγωγή SQL Query με το gemini-2.5-flash
        sql_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=db_schema_prompt,
                temperature=0.0
            )
        )
        raw_generated_sql = sql_response.text.strip()
        
        # Step B: Έλεγχος & Επαλήθευση SQL (Guardrail Layer)
        conn = get_db_connection()
        is_valid, validation_result = validate_and_verify_sql(raw_generated_sql, conn)
        
        if not is_valid:
            print(validation_result)
            return f"❌ Αποτυχία Επαλήθευσης: {validation_result}"
            
        generated_sql = validation_result
        print(f"🤖 Verified SQL ready for production:\n{generated_sql}\n")

        # Εκτέλεση ασφαλούς πλέον Query
        cursor = conn.cursor()
        cursor.execute(generated_sql)
        query_results = cursor.fetchall()
        
        colnames = [desc[0] for desc in cursor.description]
        results_as_dict = [dict(zip(colnames, row)) for row in query_results]
        cursor.close()

        # Step C: Ερμηνεία Αποτελεσμάτων & Παραγωγή Business Αναφοράς
        interpretation_prompt = f"""
        You are a Maritime AI & Analytics Engineer. Translate the following SQL query results into a professional, concise business answer in Greek.
        
        User Query: {user_query}
        SQL Executed: {generated_sql}
        Raw Results from Database: {json.dumps(results_as_dict, default=str)}
        
        Provide context like average speeds, fuel usage, and explain *why* (e.g., bad weather effect) based strictly on the data.
        """
        
        ai_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=interpretation_prompt,
            config=types.GenerateContentConfig(
                system_instruction="Απάντησε στα Ελληνικά με επαγγελματικό ναυτιλιακό ύφος.",
                temperature=0.3
            )
        )
        final_answer = ai_response.text.strip()

        # Step D: Vectorization & Logging (Με προστασία σφάλματος / Fault Tolerance)
        try:
            raw_embedding = generate_embedding(user_query)
            formatted_embedding = str(list(raw_embedding))
        except Exception as embed_error:
            print(f"⚠️ Warning: Το embedding απέτυχε ({embed_error}). Καταγραφή log χωρίς vector...")
            formatted_embedding = None

        # Αποθήκευση του Session Log στη βάση δεδομένων
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ai_chat_logs (user_query, sql_generated, ai_response, query_embedding)
            VALUES (%s, %s, %s, %s);
            """,
            (user_query, generated_sql, final_answer, formatted_embedding)
        )
        conn.commit()
        cursor.close()

        return final_answer

    except Exception as e:
        return f"❌ Σφάλμα κατά την εκτέλεση: {str(e)}"
    finally:
        if conn:
            conn.close()

# --- ΔΟΚΙΜΑΣΤΙΚΗ ΕΚΤΕΛΕΣΗ ---
if __name__ == "__main__":
    test_query = "Ποιο πλοίο είχε την χειρότερη απόδοση σε καιρό πάνω από 6 Μποφόρ τον Ιούνιο;"
    
    print(f"🚀 User Question: '{test_query}'\n")
    response = text_to_sql_agent(test_query)
    print(f"💡 AI Professional Response:\n{response}")