import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MONGO_URI")

if not uri:
    raise RuntimeError("MONGO_URI not found in .env")

client = MongoClient(uri)
print("✅ Συνδέθηκες επιτυχώς στο MongoDB Atlas!")
print(f"📌 Λίστα βάσεων: {client.list_database_names()}")