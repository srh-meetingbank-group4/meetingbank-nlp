import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# 1. Establish connection to your PostgreSQL database
try:
    conn = psycopg2.connect(
        host="localhost", 
        dbname="nlp", 
        user="postgres", 
        password="admin"
    )
except Exception as e:
    print(f"Error connecting to database: {e}")

# 2. Optimized SQL Query
# We clean the text, remove noise, and rank top 5 entities per city inside SQL.
query = """
WITH cleaned_entities AS (
    SELECT
        m.city,
        LOWER(TRIM(SPLIT_PART(entity.key, ' (', 1))) AS entity_name,
        entity.value::INT AS mention_count,
        LOWER(SPLIT_PART(entity.key, ' (', 2)) AS entity_type
    FROM meetings_metadata m
    JOIN nlp_summary_by_meeting n ON m.meeting_id = n.meeting_id,
    LATERAL jsonb_each_text(n.entities) AS entity
    WHERE 
        LENGTH(TRIM(entity.key)) > 3
        AND entity.key NOT ILIKE '%agenda item%'
        AND entity.key NOT ILIKE '%chair%'
        AND entity.key NOT ILIKE '%item%'
        AND entity.key NOT ILIKE '%section%'
        AND entity.key NOT ILIKE '%minutes%'
),
ranked_entities AS (
    SELECT 
        city, 
        entity_name, 
        mention_count, 
        entity_type,
        RANK() OVER (PARTITION BY city ORDER BY mention_count DESC) as rank_in_city
    FROM cleaned_entities
)
SELECT * FROM ranked_entities 
WHERE rank_in_city <= 5;
"""

# 3. Load data into Pandas
df = pd.read_sql(query, conn)
conn.close()

# 4. Generate Professional Visualizations
# We create a separate plot for each city to solve the scale issues.
cities = df["city"].unique()

# Define a color map for entity types to keep the visual meaning
type_colors = {
    'person)': 'skyblue', 
    'org)': 'orange', 
    'gpe)': 'red', 
    'law)': 'green'
}

for city in cities:
    # Filter and sort data for the current city
    city_df = df[df["city"] == city].sort_values("mention_count", ascending=True)
    
    plt.figure(figsize=(10, 5))
    
    # Apply colors based on entity type
    bar_colors = [type_colors.get(t, 'grey') for t in city_df["entity_type"]]
    
    bars = plt.barh(city_df["entity_name"], city_df["mention_count"], color=bar_colors)
    
    # Add data labels to the end of each bar for clarity
    for bar in bars:
        width = bar.get_width()
        plt.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2, 
                 f'{int(width)}', va='center')

    plt.title(f"Top 5 Meaningful Entities — {city.title()}", fontsize=14, fontweight='bold')
    plt.xlabel("Mention Count", fontsize=12)
    plt.ylabel("Entity Name", fontsize=12)
    
    # Add a custom legend for entity types
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color=c, lw=4, label=t.replace(')', '').upper()) 
                       for t, c in type_colors.items() if t in city_df["entity_type"].values]
    plt.legend(handles=legend_elements, title="Entity Type", loc='lower right')
    
    plt.tight_layout()
    plt.show()