# Enterprise Fleet Analytics & AI Copilot 🚢🤖

An enterprise-grade maritime analytics platform and AI assistant that processes multi-million row fleet telemetry data, generates operational insights using a **Text-to-SQL AI Agent**, exposes data via a **FastAPI REST API**, and visualizes key performance indicators (KPIs) through an interactive **Power BI Dashboard**.

## 🌟 Key Features
* **AI Copilot (Text-to-SQL):** Converts natural language queries into safe, production-ready PostgreSQL syntax using the official Google GenAI SDK (`gemini-2.5-flash`).
* **Production Guardrail Layer:** Employs explicit SQL injection blocking using regex patterns and structural validation via PostgreSQL `EXPLAIN` query execution planning before execution.
* **Input Validation & Function Calling:** Utilizes Pydantic models for strict type-checking and automated Gemini Function Calling to interface safely with DB backend endpoints.
* **Scalable Data Pipeline:** Custom Python data simulation script utilizing Pandas and NumPy vectorization to efficiently seed **100,000+ telemetry rows** into PostgreSQL.
* **Interactive Power BI Dashboard:** Real-time metrics visualization focusing on vessel fuel efficiency, cargo capacity allocation, and adverse weather impact analysis.
* **MLOps Logging:** Automated performance logging capturing user questions, LLM latency metrics, and execution metadata directly into database transaction logs.

## 🏗️ Architecture & Tech Stack
* **Language:** Python 3.10+
* **Frameworks:** FastAPI, Pydantic
* **AI Ecosystem:** Google GenAI SDK (`gemini-2.5-flash`, `gemini-embedding-2`), OpenAI Compatibility Layer
* **Database:** PostgreSQL (Hosted via Docker Container)
* **Data Science:** Pandas, NumPy, Psycopg2
* **Business Intelligence:** Microsoft Power BI Desktop

## 📊 Database Schema & Optimization
The solution utilizes a highly optimized relational Star Schema:
* `vessels`: Contains core fleet structural data (ID, Name, Type, DWT, Built Year).
* `telemetry_logs`: Stores 100k+ rows of real-time sensor metrics (Speed, Fuel Consumption, Weather/Beaufort Scale, Cargo Weight, Route Status).
* `ai_chat_logs`: Implements MLOps telemetry, logging LLM user queries, vector embeddings, generated SQL code, and API call latency.

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/dimitristheodoropoulos/enterprise-fleet-analytics.git](https://github.com/dimitristheodoropoulos/enterprise-fleet-analytics.git)
   cd enterprise-fleet-analytics

   Configure Environment Variables:
The application securely fetches the Gemini API credentials using environment variables. Set your key in your terminal before running the application:

# On Windows (PowerShell)
$env:GEMINI_API_KEY="your_actual_api_key_here"

Populate the Database:
Ensure your PostgreSQL docker container is up and running, then execute the data pipeline script to seed the database with 100,000 production-scale telemetry records:

python database/generate_data.py

Start the FastAPI Backend Server:

uvicorn main:app --reload

Execute the AI Chatbot Agent:

python chatbot_agent.py

📈 Power BI Insights
Open the Enterprise_Fleet_Analytics.pbix file in Power BI Desktop and hit Refresh to explore live aggregated data pipelines:

Fuel efficiency degradation maps against high Beaufort weather states.

Fuel consumption trends by hull type and asset age profile.