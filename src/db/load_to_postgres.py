import pandas as pd
import psycopg2
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CSV_FILE = PROCESSED_DIR / "meetingbank_train_cleaned.csv"

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="meetingbank",
    user="postgres",
    password="admin"
)
cur = conn.cursor()

print(f"Loading meetings from {CSV_FILE}...")

df = pd.read_csv(CSV_FILE)

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO meetings (meeting_title, meeting_summary)
        VALUES (%s, %s)
    """, (
        row["id"],        # using meeting id as title placeholder
        row["summary"]
    ))

conn.commit()
cur.close()
conn.close()

print("✅ Meetings table loaded successfully")