import os
from google import genai

# Διαβάζουμε το κλειδί απευθείας (αφού κάναμε source airflow/.env)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found. Make sure you sourced the .env file first.")

# Το νέο στιλ του Google GenAI client
client = genai.Client(api_key=api_key)

# Το μοτίβο που βρήκε το pipeline σου
patterns = """
Topic: artificial_intelligence
en.wikipedia: 100%
ja.wikipedia: 3.9% (lagging)

Topic: machine_translation
en.wikipedia: 100%
ja.wikipedia: 5.9% (lagging)
"""

prompt = f"""
I am a Data Analyst investigating why Japanese Wikipedia has significantly fewer pageviews compared to English.
Here is the data pattern:
{patterns}

Given that this is a multilingual content platform, please generate:
1. Three plausible hypotheses for why this gap exists (relating to translation quality, reader population, or language-specific AI usage).
2. Three specific data sources or metrics I should analyze next to test these hypotheses.
3. A brief evaluation of whether this pageview gap *could* indicate a translation quality issue, and why/why not.

Present the answer in a clear, plain-language format suitable for a Product Manager or Linguist.
"""

print("🔄 Generating analysis with new Gemini client...")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)

print("\n--- LLM-Generated Analysis ---\n")
print(response.text)