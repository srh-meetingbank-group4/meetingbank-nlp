from transformers import pipeline
from pymongo import MongoClient
from tqdm import tqdm

# Sentiment pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]
turns_col = db["turns"]
sentiment_col = db["nlp_sentiment"]

# Clean previous sentiment
sentiment_col.delete_many({})

# Get total number of documents
total_docs = turns_col.count_documents({})

print("Running sentiment analysis (turn-level)...")

# Create a progress bar
pbar = tqdm(total=total_docs)

for doc in turns_col.find({}, {"meeting_id": 1, "turn_id": 1, "text": 1}):
    text = doc.get("text", "")
    meeting_id = doc.get("meeting_id")
    turn_id = doc.get("turn_id")

    if not text.strip():
        pbar.update(1)
        continue

    try:
        result = sentiment_pipeline(text[:512])[0]

        sentiment_col.insert_one({
            "meeting_id": meeting_id,
            "turn_id": turn_id,
            "label": result["label"],
            "score": result["score"]
        })

    except Exception:
        pass

    # Update the progress bar
    pbar.update(1)

pbar.close()
print("Sentiment analysis complete.")