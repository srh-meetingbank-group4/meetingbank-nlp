import json
import psycopg2
import pandas as pd
from datetime import datetime

# 1️⃣ Read your MongoDB exported JSON
with open(r'F:\SRH Munich\1st sem\Data engineering\Local Repo\meetingbank-nlp\data\collections data\meetingbank.meetings.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Normalize JSON
df = pd.json_normalize(data)

# 2️⃣ Sanitize DataFrame
# Fill NaN with None (so psycopg2 inserts NULL)
df = df.where(pd.notnull(df), None)

# Convert date column to datetime.date if not None
def parse_date(d):
    if d is None:
        return None
    try:
        return pd.to_datetime(d).date()
    except Exception:
        return None

df['date'] = df['date'].apply(parse_date)

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

# 4️⃣ Insert into nlp_meetings
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO nlp_meetings(meeting_id, city, date, agenda)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (meeting_id) DO NOTHING;
    """, (
        int(row['meeting_id']),
        row.get('city'),
        row.get('date'),
        row.get('agenda')
    ))

# 5️⃣ Commit and close
conn.commit()
cur.close()
conn.close()

print("Data imported successfully!")