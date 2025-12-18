from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

raw_entities = db["nlp_entities"]
meetings = db["meetings"]
normalized = db["nlp_entities_normalized"]

normalized.delete_many({})

print("Normalizing entities...")

for doc in raw_entities.find({}):
    meeting_id = doc["meeting_id"]
    entities = doc.get("entities", {})

    meeting = meetings.find_one({"meeting_id": meeting_id})
    city = meeting.get("city") if meeting else None

    for key, count in entities.items():
        if "(" not in key:
            continue

        text, label = key.rsplit(" (", 1)
        entity_type = label.replace(")", "").strip()
        entity_text = text.strip()

        normalized.insert_one({
            "meeting_id": meeting_id,
            "city": city,
            "entity_type": entity_type,
            "entity_text": entity_text,
            "count": count
        })

print("✅ Entity normalization complete.")