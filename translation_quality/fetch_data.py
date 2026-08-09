"""
fetch_data.py

Provides a unified data loader that reads from MongoDB if available,
otherwise falls back to the local CSV file.

This enables graceful degradation: if the database is unreachable
(for any reason), the analysis still runs on the CSV.
"""

import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

# Optional: set this to False to force CSV mode for development
USE_MONGO = True   # Set to False to ignore MongoDB and use CSV

def get_data():
    """
    Load translation events data.
    Returns a pandas DataFrame.
    """
    # If we explicitly want CSV mode, skip MongoDB
    if not USE_MONGO:
        print("⚙️  Using CSV mode (USE_MONGO = False)")
        return pd.read_csv("translation_events.csv")

    # Try to load from MongoDB
    try:
        # Load .env from the parent folder or from mongodb/.env
        env_path = os.path.join(os.path.dirname(__file__), "..", "mongodb", ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            load_dotenv()  # fallback to current directory

        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI not found in .env")

        # --- FIX: Προσθήκη παραμέτρων SSL ---
        if "tlsAllowInvalidCertificates" not in uri:
            separator = "&" if "?" in uri else "?"
            uri += f"{separator}tlsAllowInvalidCertificates=true"

        client = MongoClient(uri)
        # Ping to verify connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")

        db = client['translation_pipeline']
        collection = db['translation_events']

        # Fetch data (limit to avoid memory issues, but we have only 4k rows)
        cursor = collection.find({}, {'_id': 0})  # exclude MongoDB's _id
        df = pd.DataFrame(list(cursor))

        if df.empty:
            print("⚠️  No data found in MongoDB. Falling back to CSV.")
            return pd.read_csv("translation_events.csv")

        print(f"✅ Loaded {len(df)} rows from MongoDB")
        return df

    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("⚙️  Falling back to CSV file...")
        return pd.read_csv("translation_events.csv")