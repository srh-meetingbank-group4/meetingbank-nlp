from pymongo import MongoClient
from tqdm import tqdm
from transformers import pipeline

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

turns_collection = db["turns"]
meetings_collection = db["meetings"]
sentiment_collection = db["nlp_sentiment"]

# Load sentiment pipeline
sentiment_model = pipeline("sentiment-analysis")

# Get all meetings
meetings = list(meetings_collection.find({}))

for meeting in tqdm(meetings, desc="Processing meetings"):
    meeting_id = meeting["meeting_id"]
    city = meeting["city"]

    # Fetch all turns for this meeting
    turns = list(turns_collection.find({"meeting_id": meeting_id}))

    if not turns:
        continue

    # Analyze sentiment for each turn
    for turn in turns:
        text = turn["text"]
        if not text.strip():
            continue

        sentiment_result = sentiment_model(text[:512])[0]  # limit to 512 chars
        sentiment_doc = {
            "meeting_id": meeting_id,
            "turn_id": turn["turn_id"],
            "city": city,
            "text": text,
            "label": sentiment_result["label"],
            "score": float(sentiment_result["score"])
        }
        sentiment_collection.insert_one(sentiment_doc)

print("✅ Sentiment aggregation complete!")