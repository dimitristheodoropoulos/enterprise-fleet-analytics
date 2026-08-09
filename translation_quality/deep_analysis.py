"""
deep_analysis.py

Performs deep root-cause analysis, hypothesis testing, and statistical 
segmentation on the translation fleet analytics data pulled from MongoDB.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fetch_data import get_data

# Ρύθμιση αισθητικής γραφημάτων
sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

def run_analysis():
    print("🔄 Loading data from MongoDB Atlas via fetch_data pipeline...")
    df = get_data()
    
    if df.empty:
        print("❌ No data available for analysis.")
        return

    print(f"📊 Dataset loaded successfully. Total records: {len(df)}")
    print("=" * 60)

    # 1. Βασική Στατιστική Επισκόπηση & Κατανομές
    print("\n🔍 1. Statistical Overview (Quality Score & Edit Distance):")
    numeric_df = df.select_dtypes(include=[np.number])
    print(numeric_df.describe())

    # 2. Ανάλυση ανά Γλωσσικό Ζεύγος & AI Provider
    print("\n🌍 2. Performance Breakdown by Language Pair & AI Provider:")
    pair_analysis = df.groupby(['language_pair', 'ai_model_provider']).agg(
        avg_edit_distance=('user_edit_distance', 'mean'),
        median_edit_distance=('user_edit_distance', 'median'),
        avg_quality_score=('quality_score', 'mean'),
        total_events=('event_id', 'count')
    ).reset_index().sort_values(by='avg_edit_distance', ascending=False)
    
    print(pair_analysis.to_string(index=False))

    # 3. Correlation Analysis (Signal vs Noise)
    print("\n📈 3. Correlation Matrix (Identifying root drivers):")
    corr_matrix = numeric_df.corr()
    print(corr_matrix[['user_edit_distance', 'quality_score']])

    # 4. Content Type Impact on Quality
    print("\n📑 4. Impact of Content Type on User Edits & Quality:")
    content_analysis = df.groupby('content_type').agg(
        avg_edit=('user_edit_distance', 'mean'),
        avg_quality=('quality_score', 'mean'),
        sample_size=('event_id', 'count')
    ).reset_index()
    print(content_analysis.to_string(index=False))

    # 5. Traffic Volume Impact Analysis (New addition for full job alignment)
    print("\n🚦 5. Impact of Traffic Volume on Latency & Quality:")
    if 'traffic_volume' in df.columns:
        traffic_analysis = df.groupby('traffic_volume').agg(
            avg_latency=('latency_ms', 'mean'),
            avg_quality=('quality_score', 'mean'),
            avg_edit=('user_edit_distance', 'mean'),
            sample_size=('event_id', 'count')
        ).reset_index().sort_values(by='avg_latency', ascending=False)
        print(traffic_analysis.to_string(index=False))
    else:
        print("⚠️ 'traffic_volume' column not found in dataset.")

    # --- 6. VISUALIZATIONS ---
    print("\n🎨 Generating analytical charts...")
    
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df, 
        x='language_pair', 
        y='user_edit_distance', 
        hue='ai_model_provider', 
        errorbar=None, 
        palette='muted'
    )
    plt.title('Average User Edit Distance by Language Pair & AI Provider', fontsize=14, fontweight='bold')
    plt.xlabel('Language Pair', fontsize=12)
    plt.ylabel('Average User Edit Distance', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='AI Provider')
    plt.savefig('edit_distance_by_pair.png', dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=df, 
        x='content_type', 
        y='quality_score', 
        palette='Set2'
    )
    plt.title('Quality Score Distribution across Content Types', fontsize=14, fontweight='bold')
    plt.xlabel('Content Type', fontsize=12)
    plt.ylabel('Quality Score', fontsize=12)
    plt.savefig('quality_by_content_type.png', dpi=300)
    plt.close()

    print("\n✅ Analysis complete! Charts saved.")

if __name__ == '__main__':
    run_analysis()