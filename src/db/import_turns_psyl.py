import json
import psycopg2
import pandas as pd

# 1️⃣ Read your MongoDB exported JSON
with open(r'F:\SRH Munich\1st sem\Data engineering\Local Repo\meetingbank-nlp\data\collections data\meetingbank.turns.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.json_normalize(data)

# 2️⃣ Sanitize DataFrame
df = df.where(pd.notnull(df), None)

# Optional: check columns
print(df.head())

# 3️⃣ Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="meetingbank",
    user="postgres",
    password="admin"
)
cur = conn.cursor()

# 4️⃣ Insert into turns table
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO nlp_turns(turn_id, meeting_id, text)
        VALUES (%s, %s, %s)
        ON CONFLICT (turn_id) DO NOTHING;
    """, (
        int(row['turn_id']),
        int(row['meeting_id']),
        row.get('text')
    ))

# 5️⃣ Commit and close
conn.commit()
cur.close()
conn.close()

print("Turns imported successfully!")