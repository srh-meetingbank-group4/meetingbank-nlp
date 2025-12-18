import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

conn = psycopg2.connect(
    host="localhost", dbname="nlp", user="postgres", password="admin"
)

# JOIN ensures we get city names from metadata and sentiment from the NLP table
query = """
SELECT
    m.city,
    ROUND(STDDEV(n.avg_sentiment)::numeric, 3) AS sentiment_volatility
FROM meetings_metadata m
JOIN nlp_summary_by_meeting n ON m.meeting_id = n.meeting_id
GROUP BY m.city
ORDER BY sentiment_volatility DESC;
"""

df = pd.read_sql(query, conn)
conn.close()

# Drop cities with only 1 meeting (where volatility is NaN)
df = df.dropna(subset=["sentiment_volatility"])

if df.empty:
    print("Not enough data to calculate volatility. Need at least 2 meetings per city.")
else:
    plt.figure(figsize=(10, 6))
    # Use a specific color to make it look distinct from your other charts
    plt.bar(df["city"], df["sentiment_volatility"], color='teal')
    
    plt.title("Sentiment Volatility: Which City has the Most 'Emotional' Meetings?", fontsize=14)
    plt.xlabel("City", fontsize=12)
    plt.ylabel("Volatility (Standard Deviation)", fontsize=12)
    
    # Adding a helpful note for the professor
    plt.figtext(0.5, -0.05, "Note: Cities with only 1 meeting are excluded (no variance possible).", 
                ha="center", fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.show()