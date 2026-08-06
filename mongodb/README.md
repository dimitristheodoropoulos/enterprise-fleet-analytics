# MongoDB Atlas Connection for Translation Pipeline

This folder contains the configuration and client scripts to connect to the **MongoDB Atlas (free M0 Sandbox)** cluster.

## Why MongoDB (NoSQL)?
- Stores raw JSON responses from external APIs (e.g., LibreTranslate MT requests).
- Demonstrates the ability to work with both **NoSQL** and **SQL** databases in the same pipeline (MongoDB → Supabase).

## Files
- `.env`: Contains the `MONGO_URI` connection string.
- `mongo_client.py`: Simple connection test script.

## Usage
```bash
pip install pymongo python-dotenv
python3 mongo_client.py

---

### 🛡️ Βήμα 4: Πρόσθεσε το `.env` στο `.gitignore` (ΚΡΙΣΙΜΟ!)
Για να μην ανέβει ο κωδικός σου στο GitHub, δώσε αυτή την εντολή από τη ρίζα του project:
```bash
cd ~/Desktop/enterprise-fleet-analytics
echo "mongodb/.env" >> .gitignore