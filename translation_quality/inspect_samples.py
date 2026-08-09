"""
inspect_samples.py

Telemetry outlier inspection pipeline. Since the dataset tracks fleet 
performance metrics rather than raw text, this script profiles the 
operational characteristics of worst-performing translation events.
"""

from fetch_data import get_data

def inspect_telemetry_outliers(top_n=5):
    print("🔄 Loading data from MongoDB Atlas...")
    df = get_data()
    
    if df.empty:
        print("❌ No data available.")
        return

    print(f"\n🔍 Inspecting telemetry profile of top {top_n} quality outliers (Highest Edit Distance)...")
    
    # Ταξινόμηση για τα 5 χειρότερα συμβάντα βάσει edit distance
    outliers = df.sort_values(by='user_edit_distance', ascending=False).head(top_n)
    
    for idx, row in outliers.iterrows():
        print("=" * 80)
        print(f"📌 Event ID: {row.get('event_id')} | Timestamp: {row.get('timestamp')}")
        print(f"🌍 Language Pair: {row.get('language_pair')} | Provider: {row.get('ai_model_provider')} ({row.get('ai_model_version')})")
        print(f"📑 Content Type: {row.get('content_type')} | Customer Tier: {row.get('customer_tier')} | Traffic: {row.get('traffic_volume')}")
        print(f"📏 Sentence Length: {row.get('sentence_length_words')} words | Latency: {row.get('latency_ms')} ms")
        print(f"❌ Quality Score: {row.get('quality_score'):.3f} | ✍️ User Edit Distance: {row.get('user_edit_distance'):.3f}")
    print("=" * 80)

if __name__ == '__main__':
    inspect_telemetry_outliers()