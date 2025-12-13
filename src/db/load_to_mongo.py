from pymongo import MongoClient
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank_db"]

# Example: load cleaned train CSV
train_file = PROCESSED_DIR / "meetingbank_train_cleaned.csv"
df = pd.read_csv(train_file)

# Insert into MongoDB collection
collection = db["meetings"]
records = df.to_dict(orient="records")
collection.insert_many(records)

print("✅ Data loaded into MongoDB!")