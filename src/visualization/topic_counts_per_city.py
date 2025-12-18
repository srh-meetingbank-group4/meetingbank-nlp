import psycopg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost", dbname="nlp", user="postgres", password="admin"
)

# Load topic counts per city
query = """
SELECT 
    m.city, 
    n.dominant_topic, 
    COUNT(*) AS topic_count
FROM 
    meetings_metadata m
JOIN 
    nlp_summary_by_meeting n
ON 
    m.meeting_id = n.meeting_id
GROUP BY 
    m.city, n.dominant_topic
ORDER BY 
    m.city, n.dominant_topic;
"""
df = pd.read_sql(query, conn)
conn.close()

# Pivot for stacked bar chart
df_pivot = df.pivot(index='city', columns='dominant_topic', values='topic_count').fillna(0)

# Plot
plt.figure(figsize=(10,6))
df_pivot.plot(kind='bar', stacked=True, colormap='tab20')
plt.title("Topic Distribution Across Cities", fontsize=16)
plt.xlabel("City")
plt.ylabel("Number of Meetings")
plt.xticks(rotation=45)
plt.legend(title="Topic ID", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()