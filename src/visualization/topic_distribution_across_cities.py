import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Load data
conn = psycopg2.connect(
    host="localhost", dbname="nlp", user="postgres", password="admin"
)

query = """
SELECT 
    m.city,
    n.dominant_topic,
    COUNT(*) AS topic_count
FROM meetings_metadata m
JOIN nlp_summary_by_meeting n
ON m.meeting_id = n.meeting_id
GROUP BY m.city, n.dominant_topic;
"""

df = pd.read_sql(query, conn)
conn.close()

# Pivot table
pivot = df.pivot_table(
    index="city",
    columns="dominant_topic",
    values="topic_count",
    fill_value=0
)

# Convert to percentages
pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

# Plot
pivot_pct.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 7)
)

plt.title("Topic Distribution Across Cities (Percentage View)", fontsize=16)
plt.ylabel("Percentage of Meetings (%)")
plt.xlabel("City")
plt.legend(title="Topic ID", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()