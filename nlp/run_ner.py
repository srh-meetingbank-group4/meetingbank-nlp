import spacy
from pymongo import MongoClient
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

turns_col = db["turns"]
meetings_col = db["meetings"]
entities_col = db["nlp_entities"]

entities_col.delete_many({})

# Map meeting_id -> city
meeting_city = {
    m["meeting_id"]: m["city"]
    for m in meetings_col.find({}, {"meeting_id": 1, "city": 1})
}

entity_counter = defaultdict(int)

print("Running NER across all meetings...")

for doc in turns_col.find({}, {"meeting_id": 1, "text": 1}):
    meeting_id = doc["meeting_id"]
    city = meeting_city.get(meeting_id)

    if not city:
        continue

    parsed = nlp(doc["text"])

    for ent in parsed.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LAW"]:
            key = (meeting_id, city, ent.label_, ent.text)
            entity_counter[key] += 1

# Insert aggregated results
for (mid, city, etype, text), count in entity_counter.items():
    entities_col.insert_one({
        "meeting_id": mid,
        "city": city,
        "entity_type": etype,
        "entity_text": text,
        "count": count
    })

print("NER aggregation complete.")