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

cur.execute("SELECT meeting_id FROM meetings ORDER BY meeting_id")
meeting_ids = [row[0] for row in cur.fetchall()]

for meeting_id, (_, row) in zip(meeting_ids, df.iterrows()):
    cur.execute(
        "INSERT INTO metadata (meeting_id, key, value) VALUES (%s, %s, %s)",
        (meeting_id, "uid", row["uid"])
    )
    cur.execute(
        "INSERT INTO metadata (meeting_id, key, value) VALUES (%s, %s, %s)",
        (meeting_id, "summary", row["summary"])
    )
    cur.execute(
        "INSERT INTO metadata (meeting_id, key, value) VALUES (%s, %s, %s)",
        (meeting_id, "transcript", row["transcript"])
    )

conn.commit()
cur.close()
conn.close()

print("✅ Metadata loaded correctly")