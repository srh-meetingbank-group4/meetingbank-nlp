import pandas as pd
import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_FILE = BASE_DIR / "data" / "processed" / "meetingbank_train_cleaned.csv"

conn = psycopg2.connect(
    host="localhost",
    database="meetingbank",
    user="postgres",
    password="admin"
)
cur = conn.cursor()

df = pd.read_csv(CSV_FILE)

for _ in range(len(df)):
    cur.execute("""
        INSERT INTO meetings (city, date, duration_minutes)
        VALUES (NULL, NULL, NULL)
        RETURNING meeting_id
    """)

conn.commit()
cur.close()
conn.close()

print("✅ Meetings placeholder rows created")