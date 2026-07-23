import json
import pandas as pd

# 1. Διάβασε το φύλλο '04_AI_Training_Data' από το Excel σου
excel_file = "Fleet_Telemetry_Analysis_v1.xlsx"
sheet_name = "04_AI_Training_Data"

df = pd.read_excel(excel_file, sheet_name=sheet_name)

# 2. Άνοιξε ένα αρχείο .jsonl για εγγραφή
output_jsonl = "fleet_ai_training_data.jsonl"

with open(output_jsonl, "w", encoding="utf-8") as f:
  # Υποθέτουμε ότι οι στήλες λέγονται 'Prompt / User Query' και 'Ground Truth AI Response'
  for _, row in df.iterrows():
    # Δημιουργία του dictionary σύμφωνα με το standard format για LLMs
    record = {
        "prompt": str(row["Prompt / User Query"]),
        "response": str(row["Ground Truth AI Response"]),
    }
    # Εγγραφή κάθε γραμμής ως ξεχωριστή γραμμή JSON (JSONL)
    f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(
    f"Επιτυχής εξαγωγή! Το αρχείο '{output_jsonl}' δημιουργήθηκε με επιτυχία."
)