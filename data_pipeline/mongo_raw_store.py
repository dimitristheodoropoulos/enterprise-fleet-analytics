"""
mongo_raw_store.py

Stores the raw, unflattened JSON response from each Wikimedia API call into
MongoDB Atlas -- this is the genuine NoSQL step in the pipeline: raw,
semi-structured API responses land here first, and only the cleaned,
flattened rows go on to Postgres (via load_to_supabase.py).

Reuses the same MONGO_URI used by the standalone connectivity test in
../mongodb/mongo_client.py.
"""

import os
from datetime import datetime, timezone

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError(
            "MONGO_URI not found in environment. Add it to data_pipeline/.env "
            "(same value as in mongodb/.env)."
        )
    _client = MongoClient(uri)
    db = _client["translation_pipeline"]
    _collection = db["raw_pageview_responses"]
    return _collection


def store_raw_response(topic: str, project: str, article: str, start: str, end: str, payload: dict) -> None:
    """Insert one raw API response document. Never raises -- a storage
    hiccup here should not break the extract run; it just means this one
    response wasn't archived."""
    try:
        collection = _get_collection()
        collection.insert_one(
            {
                "topic": topic,
                "project": project,
                "article": article,
                "range_start": start,
                "range_end": end,
                "fetched_at": datetime.now(timezone.utc),
                "raw_response": payload,
            }
        )
    except Exception as e:
        print(f"  [mongo] warning: could not store raw response for {topic}/{project}: {e}")