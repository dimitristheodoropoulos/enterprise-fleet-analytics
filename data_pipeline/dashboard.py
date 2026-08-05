import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px

# Σύνδεση με τη βάση
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    st.error("DATABASE_URL is not set.")
    st.stop()

conn = psycopg2.connect(db_url, sslmode='require')

# Ανάγνωση δεδομένων
df = pd.read_sql_query("SELECT * FROM language_coverage_gap ORDER BY topic, pct_of_top_edition DESC", conn)
conn.close()

st.set_page_config(layout="wide")
st.title("🌍 Wikipedia Pageview Coverage Dashboard")
st.markdown("Δείτε ποιες γλώσσες έχουν τη μεγαλύτερη διαφορά στην κάλυψη.")

for topic in df['topic'].unique():
    st.subheader(f"Topic: {topic.replace('_', ' ').title()}")
    topic_df = df[df['topic'] == topic]
    
    # Bar Chart
    fig = px.bar(topic_df, x='project', y='pct_of_top_edition', 
                 color='project', text='pct_of_top_edition',
                 title=f"Coverage percentage per language for {topic}")
    fig.update_layout(xaxis_title="Language Project", yaxis_title="% of Leading Edition")
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(topic_df[['project', 'total_views', 'pct_of_top_edition']])