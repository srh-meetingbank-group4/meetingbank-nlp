import pandas as pd
import psycopg2
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CSV_FILE = PROCESSED_DIR / "meetingbank_train_cleaned.csv"

# -----------------------------
# PostgreSQL connection
# -----------------------------
conn = psycopg2.connect(
    host="localhost",
    database="meetingbank",
    user="postgres",
    password="admin"  # change if needed
)
cur = conn.cursor()

print(f"Loading turns from {CSV_FILE}...")

df = pd.read_csv(CSV_FILE)

insert_query = """
    INSERT INTO turns (agenda_id, speaker_id, turn_text, start_time, end_time)
    VALUES (%s, %s, %s, %s, %s)
"""

for _, row in df.iterrows():
    cur.execute(
        insert_query,
        (
            None,                    # agenda_id
            None,                    # speaker_id
            row["transcript"],       # turn_text
            None,                    # start_time
            None                     # end_time
        )
    )

conn.commit()
cur.close()
conn.close()

print("✅ Turns loaded successfully into PostgreSQL.")
