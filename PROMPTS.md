# 📘 AI Agent Prompt Library & Adoption Guide

Αυτός ο οδηγός δημιουργήθηκε για να υποστηρίξει την υιοθέτηση (AI Adoption) του **Nautilus Maritime Analytics Agent** από τα επιχειρηματικά τμήματα (Operations, Chartering, Fleet Management) της Castor Ships.

---

## 🧠 1. System Prompt Architecture (Πώς Σκέφτεται το AI)

Ο Agent χρησιμοποιεί δύο εξειδικευμένα System Instructions για να διασφαλίσει την ακρίβεια των αποτελεσμάτων και το επαγγελματικό ύφος:

### Α. Text-to-SQL Generation Instruction
Καθοδηγεί το μοντέλο `gemini-2.5-flash` να λειτουργεί ως έμπειρος Data Analyst, περιορίζοντας τις απαντήσεις αποκλειστικά σε έγκυρη PostgreSQL χωρίς Markdown blocks.
```text
You are an expert Data Analyst for Castor Ships. Given the following PostgreSQL database schema, 
generate a valid SQL query that answers the user's request. Return ONLY the raw SQL query, no markdown, no code blocks.

Tables:
1. table: vessels (vessel_id, vessel_name, vessel_type, capacity_dwt, year_built)
2. table: telemetry_logs (log_id, vessel_id, log_date, speed_knots, fuel_consumption_tons, wind_beaufort, cargo_weight_tons, route_status)