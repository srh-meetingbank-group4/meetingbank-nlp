import json
import psycopg2
import pandas as pd

# -----------------------------
# 1️⃣ PostgreSQL connection
# -----------------------------
conn = psycopg2.connect(
    host="localhost",
    database="meetingbank",
    user="postgres",
    password="admin"
)
cur = conn.cursor()

# -----------------------------
# 2️⃣ Function to load JSON and normalize
# -----------------------------
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    return df

# -----------------------------
# 3️⃣ Import nlp_entities_normalized
# -----------------------------
df_entities = load_json(r'F:\SRH Munich\1st sem\Data engineering\Local Repo\meetingbank-nlp\data\collections data\nlp_entities_normalized.json')
print(df_entities.columns)  # print the column names

for _, row in df_entities.iterrows():
    cur.execute("""
        INSERT INTO nlp_entities_normalized(meeting_id, city, entity_type, entity_text, count)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (meeting_id) DO NOTHING;
    """, (
        int(row.get('meeting_id', 0)),
        row.get('city'),
        row.get('entity_type'),
        row.get('entity_text'),
        int(row.get('count', 0))
    ))

print("✅ nlp_entities_normalized imported successfully!")

# -----------------------------
# 4️⃣ Import nlp_sentiment_summary
# -----------------------------
df_sentiment = load_json(r'F:\SRH Munich\1st sem\Data engineering\Local Repo\meetingbank-nlp\data\collections data\nlp_sentiment_summary.json')
print(df_sentiment.columns)  # print the column names

for _, row in df_sentiment.iterrows():
    cur.execute("""
        INSERT INTO nlp_sentiment_summary(meeting_id, city, avg_sentiment, positive_ratio, negative_ratio, model)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (meeting_id) DO NOTHING;
    """, (
        int(row.get('meeting_id', 0)),
        row.get('city'),
        float(row.get('avg_sentiment', 0.0)),
        float(row.get('positive_ratio', 0.0)),
        float(row.get('negative_ratio', 0.0)),
        row.get('model')
    ))

print("✅ nlp_sentiment_summary imported successfully!")

# -----------------------------
# 5️⃣ Import entity_city_stats
# -----------------------------
df_entity_stats = load_json(r'F:\SRH Munich\1st sem\Data engineering\Local Repo\meetingbank-nlp\data\collections data\entity_city_stats.json')
print(df_entity_stats.columns)  # print the column names

for _, row in df_entity_stats.iterrows():
    cur.execute("""
        INSERT INTO entity_city_stats(city, entity_type, total_count, entity_text)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (city, entity_type) DO NOTHING;
    """, (
        row.get('city'),
        row.get('entity_type'),
        row.get('total_count'),
        row.get('entity_text')
    ))

print("✅ entity_city_stats imported successfully!")

# -----------------------------
# 6️⃣ Commit and close
# -----------------------------
conn.commit()
cur.close()
conn.close()
print("🎉 All three collections imported successfully!")