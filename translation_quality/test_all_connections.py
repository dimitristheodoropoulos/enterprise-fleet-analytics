"""
test_all_connections.py

Δοκιμάζει διάφορους τρόπους σύνδεσης στο MongoDB Atlas
για να βρει ποιος δουλεύει στο τρέχον σύστημα.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv("../mongodb/.env")
BASE_URI = os.getenv("MONGO_URI")

if not BASE_URI:
    raise RuntimeError("MONGO_URI not found in .env")

def test_connection(uri, label):
    """Δοκιμάζει μια σύνδεση με συγκεκριμένο URI και επιστρέφει True/False."""
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        print(f"✅ {label}: SUCCESS")
        return True
    except Exception as e:
        # Συνοπτικό σφάλμα, χωρίς να γεμίζουμε την οθόνη με το τεράστιο stack trace
        err_type = type(e).__name__
        err_msg = str(e)[:100]
        print(f"❌ {label}: FAILED ({err_type}: {err_msg}...)")
        return False

# 1. Original (χωρίς παραμέτρους) – συνήθως αποτυγχάνει
print("=" * 60)
print("🔍 Testing connection variants...")
print("=" * 60)

test_connection(BASE_URI, "1. Original URI")

# 2. Με certifi (σωστά certificates)
uri2 = BASE_URI
test_connection(MongoClient(uri2, tlsCAFile=certifi.where()), "2. With certifi")

# 3. Με tlsAllowInvalidCertificates=true (αγνοεί SSL errors)
separator = "&" if "?" in BASE_URI else "?"
uri3 = BASE_URI + f"{separator}tlsAllowInvalidCertificates=true"
test_connection(uri3, "3. With tlsAllowInvalidCertificates=true")

# 4. Με tlsAllowInvalidCertificates=true και certifi μαζί
try:
    client4 = MongoClient(uri3, tlsCAFile=certifi.where())
    client4.admin.command('ping')
    print("✅ 4. With both (certifi + tlsAllowInvalidCertificates): SUCCESS")
except Exception as e:
    print(f"❌ 4. With both: FAILED ({type(e).__name__})")

print("=" * 60)
print("✅ Done. Look at which one succeeded.")
print("=" * 60)