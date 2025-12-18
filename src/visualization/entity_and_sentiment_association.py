import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# 1. Database Connection
conn = psycopg2.connect(
    host="localhost", dbname="nlp", user="postgres", password="admin"
)

# 2. Query
query = """
SELECT
    m.city,
    SPLIT_PART(e.key, ' (', 1) AS entity,
    ROUND(AVG(n.avg_sentiment)::numeric, 3) AS avg_sentiment
FROM meetings_metadata m
JOIN nlp_summary_by_meeting n
    ON m.meeting_id = n.meeting_id
JOIN LATERAL jsonb_each(n.entities) AS e(key, value)
    ON TRUE
WHERE n.avg_sentiment IS NOT NULL
GROUP BY m.city, entity
HAVING COUNT(*) >= 1
ORDER BY avg_sentiment ASC
LIMIT 15;
"""

df = pd.read_sql(query, conn)
conn.close()

# 3. Final Polish Visualization
plt.figure(figsize=(14, 9)) # Slightly wider for long labels

# Professional Dark Red
bar_color = '#c0392b' 

bars = plt.barh(df["entity"], df["avg_sentiment"], color=bar_color, edgecolor='black', height=0.7)

# Add a vertical line at 0
plt.axvline(0, color='black', linewidth=1.5)

# FIX: Clean label placement
for bar in bars:
    width = bar.get_width()
    
    # We place the label slightly to the LEFT of the bar end since it's negative
    plt.text(
        width - 0.01,           # X position: slightly left of the bar end
        bar.get_y() + bar.get_height()/2, 
        f'{width:.3f}', 
        va='center', 
        ha='right',             # Align right so it stays inside the whitespace area
        fontsize=11, 
        fontweight='bold',
        color='black'           # Consistent black text
    )

# FIX: Expand X-axis so nothing is cut off
plt.xlim(df["avg_sentiment"].min() - 0.15, 0.1) 

plt.title("Entity–Sentiment Association: Significant Negative Triggers", fontsize=18, pad=25)
plt.xlabel("Average Sentiment Score", fontsize=14)
plt.ylabel("Entity Name", fontsize=14)

# Add a clean grid for readability
plt.grid(axis='x', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.show()