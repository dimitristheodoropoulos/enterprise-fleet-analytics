import os
import sys
from google import genai

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Διαβάζει το κλειδί από το περιβάλλον
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

print("🔍 Αναζήτηση διαθέσιμων Embedding Μοντέλων...")
try:
    for m in client.models.list():
        if "embed" in m.name.lower():
            print(f"-> {m.name}")
except Exception as e:
    print(f"❌ Σφάλμα κατά την ανάκτηση: {e}")