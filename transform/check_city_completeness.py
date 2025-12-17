from pymongo import MongoClient
import pandas as pd

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

meetings_col = db["meetings"]
sentiment_col = db["nlp_sentiment"]
entities_col = db["nlp_entities"]
topics_col = db["nlp_topics"]
summary_col = db["meeting_summary"]

results = []

for meeting in meetings_col.find({}, {"meeting_id": 1, "city": 1}):
    meeting_id = meeting["meeting_id"]
    city = meeting.get("city", "UNKNOWN")

    has_sentiment = sentiment_col.count_documents({"meeting_id": meeting_id}) > 0
    has_entities = entities_col.count_documents({"meeting_id": meeting_id}) > 0
    has_topics = topics_col.count_documents({"meeting_id": meeting_id}) > 0
    has_summary = summary_col.count_documents({"meeting_id": meeting_id}) > 0

    results.append({
        "meeting_id": meeting_id,
        "city": city,
        "sentiment": has_sentiment,
        "entities": has_entities,
        "topics": has_topics,
        "summary": has_summary,
        "complete": all([has_sentiment, has_entities, has_topics, has_summary])
    })

df = pd.DataFrame(results)

print("\n=== CITY / MEETING COMPLETENESS REPORT ===\n")
print(df)

print("\n=== INCOMPLETE MEETINGS ===\n")
print(df[df["complete"] == False])