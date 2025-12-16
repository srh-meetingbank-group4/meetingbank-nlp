from transformers import pipeline
from pymongo import MongoClient
from collections import defaultdict

# Sentiment pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]
turns_col = db["turns"]
sentiment_col = db["nlp_sentiment"]

sentiment_col.delete_many({})

meeting_scores = defaultdict(list)

print("Running sentiment analysis...")

for doc in turns_col.find({}, {"meeting_id": 1, "text": 1}):
    text = doc.get("text", "")
    meeting_id = doc.get("meeting_id")

    if not text.strip():
        continue

    try:
        result = sentiment_pipeline(text[:512])[0]
        score = result["score"] if result["label"] == "POSITIVE" else -result["score"]
        meeting_scores[meeting_id].append(score)
    except:
        continue

# Store aggregated sentiment
for meeting_id, scores in meeting_scores.items():
    sentiment_col.insert_one({
        "meeting_id": meeting_id,
        "avg_sentiment": sum(scores) / len(scores),
        "num_turns": len(scores)
    })

print("Sentiment analysis complete.")