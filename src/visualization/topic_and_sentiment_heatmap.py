import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# 1. Database Connection
engine = create_engine('postgresql://postgres:admin@localhost/nlp')

# 2. Optimized Query
query = """
    SELECT m.city, n.dominant_topic, 
           AVG(n.avg_sentiment) AS avg_topic_sentiment
    FROM nlp_summary_by_meeting n 
    JOIN meetings_metadata m ON n.meeting_id = m.meeting_id 
    GROUP BY m.city, n.dominant_topic;
"""

df = pd.read_sql(query, engine)
df['avg_topic_sentiment'] = pd.to_numeric(df['avg_topic_sentiment'], errors='coerce')

# 3. Pivot for heatmap
heatmap_df = df.pivot(index="city", columns="dominant_topic", values="avg_topic_sentiment")

# --- 4. PROFESSOR-PROOF ENHANCEMENTS ---

# Calculate Marginal Means (Extra row and column)
heatmap_df['CITY AVG'] = heatmap_df.mean(axis=1) # Average sentiment per city
topic_avg = heatmap_df.mean(axis=0).to_frame().T
topic_avg.index = ['TOPIC AVG']
heatmap_df = pd.concat([heatmap_df, topic_avg]) # Add average sentiment per topic row

# Sort Cities by Overall Sentiment (ascending to see most negative first)
# We keep the 'TOPIC AVG' row at the bottom
sorted_cities = heatmap_df.iloc[:-1].sort_values('CITY AVG', ascending=True)
heatmap_df = pd.concat([sorted_cities, heatmap_df.iloc[[-1]]])

# Sort Topics by Global Sentiment (excluding the CITY AVG column)
sorted_topics = heatmap_df.columns[:-1].tolist()
sorted_topics.sort(key=lambda x: heatmap_df.loc['TOPIC AVG', x])
heatmap_df = heatmap_df[sorted_topics + ['CITY AVG']]

# 5. Visualization
plt.figure(figsize=(14, 10))

# Using 'coolwarm' for perceptual accuracy (Blue = Negative, Red = Positive)
# Normalizing to -1 and 1 since sentiment typically ranges in this scale
sns.heatmap(
    heatmap_df,
    annot=True,
    fmt=".2f",           # 2 decimals is cleaner for reports
    cmap="coolwarm",     # Blue (Negative) -> White (Neutral) -> Red (Positive)
    center=0,            # Ensure 0 is the true neutral color
    vmin=-1,             # Standardize scale
    vmax=1,
    linewidths=1,
    cbar_kws={'label': 'Sentiment Score (-1 to 1)'},
    mask=heatmap_df.isnull()
)

# Highlight Marginal Aggregates (Visual distinction for the new row/column)
plt.title("Advanced Sentiment Analysis: Topics × Cities (Sorted by Global Mood)", fontsize=18, pad=25)
plt.xlabel("Topic ID (and Global Averages)", fontsize=13)
plt.ylabel("City (Sorted by Overall Mood)", fontsize=13)

# Add a visual separator for the summary row/column (optional)
plt.axhline(y=len(heatmap_df)-1, color='black', linewidth=3)
plt.axvline(x=len(heatmap_df.columns)-1, color='black', linewidth=3)

plt.tight_layout()
plt.show()