from pymongo import MongoClient
from collections import defaultdict

client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

meetings_col = db["meetings"]
sentiment_col = db["nlp_sentiment"]
entities_col = db["nlp_entities"]
summary_col = db["meeting_summary"]

# Clean previous summary
summary_col.delete_many({})

print("Building meeting_summary collection with correct aggregation...")

# Aggregate sentiment per meeting
meeting_sentiments = {}
for doc in sentiment_col.find({}):
    meeting_id = doc["meeting_id"]
    meeting_sentiments.setdefault(meeting_id, []).append(doc["score"])

# Build summary per meeting
for meeting in meetings_col.find({}):
    meeting_id = meeting["meeting_id"]
    city = meeting.get("city")
    summary_text = meeting.get("summary")

    # Aggregate sentiment
    scores = meeting_sentiments.get(meeting_id, [])
    if scores:
        avg_sentiment = sum(scores) / len(scores)
        positive_ratio = sum(1 for s in scores if s > 0) / len(scores)
        negative_ratio = sum(1 for s in scores if s < 0) / len(scores)
        num_turns = len(scores)
    else:
        avg_sentiment = None
        positive_ratio = None
        negative_ratio = None
        num_turns = 0

    # Get entities for this meeting
    entities = []
    for ent in entities_col.find({"meeting_id": meeting_id}):
        entities.append({
            "entity_type": ent["entity_type"],
            "entity_text": ent["entity_text"],
            "count": ent["count"]
        })

    # Insert into meeting_summary
    summary_col.insert_one({
        "meeting_id": meeting_id,
        "city": city,
        "summary": summary_text,
        "num_turns": num_turns,
        "avg_sentiment": avg_sentiment,
        "positive_ratio": positive_ratio,
        "negative_ratio": negative_ratio,
        "entities": entities
    })

print("meeting_summary built successfully!")