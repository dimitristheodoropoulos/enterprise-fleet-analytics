"""
upload_to_mongo.py

Uploads the CSV data to MongoDB Atlas.
Run this once to populate the database.
"""

import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env
env_path = os.path.join(os.path.dirname(__file__), "..", "mongodb", ".env")
load_dotenv(env_path)

uri = os.getenv("MONGO_URI")
if not uri:
    raise RuntimeError("MONGO_URI not found in .env")

# --- FIX: Προσθήκη παραμέτρων SSL για να αποφύγουμε το handshake error ---
# Αν το URI δεν περιέχει ήδη 'tlsAllowInvalidCertificates', το προσθέτουμε
if "tlsAllowInvalidCertificates" not in uri:
    # Αν υπάρχει ήδη '?', προσθέτουμε '&', αλλιώς '?'
    separator = "&" if "?" in uri else "?"
    uri += f"{separator}tlsAllowInvalidCertificates=true"

print("🔄 Connecting with SSL fix...")

client = MongoClient(uri)
# Δοκιμή σύνδεσης
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

db = client['translation_pipeline']
collection = db['translation_events']

# Read the CSV
df = pd.read_csv("translation_events.csv")

# Convert to list of dicts (MongoDB documents)
records = df.to_dict(orient="records")

# Clear existing data (to avoid duplicates)
collection.delete_many({})

# Insert
result = collection.insert_many(records)

print(f"✅ Uploaded {len(result.inserted_ids)} documents to MongoDB Atlas.")
print("📂 Database: translation_pipeline, Collection: translation_events")