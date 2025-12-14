import pandas as pd
from pymongo import MongoClient
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CSV_FILE = PROCESSED_DIR / "meetingbank_train_cleaned.csv"

client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

meetings_col = db["meetings"]
turns_col = db["turns"]

print("Reading CSV...")
df = pd.read_csv(CSV_FILE)

MEETING_ID = 1

print("Upserting meeting metadata...")
meetings_col.delete_many({"meeting_id": MEETING_ID})
meetings_col.insert_one({
    "meeting_id": MEETING_ID,
    "dataset": "MeetingBank",
    "split": "train",
    "num_turns": len(df)
})

print("Loading turns...")
turns_col.delete_many({"meeting_id": MEETING_ID})

bulk = []
for idx, row in df.iterrows():
    bulk.append({
        "meeting_id": MEETING_ID,
        "turn_id": idx + 1,
        "text": row["transcript"]
    })

turns_col.insert_many(bulk)

print("✅ MongoDB meetings + turns loaded successfully.")