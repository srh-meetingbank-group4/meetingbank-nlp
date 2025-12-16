import spacy
from pymongo import MongoClient
from collections import defaultdict

# Load spaCy with disabled components for speed
nlp = spacy.load("en_core_web_sm", disable=["parser", "lemmatizer", "attribute_ruler"])

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]
turns_col = db["turns"]
entities_col = db["nlp_entities"]

entities_col.delete_many({})

meeting_entities = defaultdict(lambda: defaultdict(int))

MAX_CHARS = 1000   # VERY IMPORTANT
BATCH_SIZE = 100

print("Running NER on transcripts (optimized)...")

cursor = turns_col.find({}, {"meeting_id": 1, "text": 1})

batch = []
count = 0

for doc in cursor:
    text = doc.get("text", "")
    meeting_id = doc.get("meeting_id")

    if not text:
        continue

    # Truncate text for scalability
    text = text[:MAX_CHARS]

    batch.append((meeting_id, text))

    if len(batch) >= BATCH_SIZE:
        for meeting_id, text in batch:
            parsed = nlp(text)
            for ent in parsed.ents:
                if ent.label_ in ["PERSON", "ORG", "GPE", "LAW", "MONEY"]:
                    meeting_entities[meeting_id][f"{ent.text} ({ent.label_})"] += 1

        count += len(batch)
        print(f"Processed {count} turns...")
        batch.clear()

# Process remaining
for meeting_id, text in batch:
    parsed = nlp(text)
    for ent in parsed.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LAW", "MONEY"]:
            meeting_entities[meeting_id][f"{ent.text} ({ent.label_})"] += 1

# Store results incrementally
for meeting_id, ents in meeting_entities.items():
    entities_col.insert_one({
        "meeting_id": meeting_id,
        "entities": dict(ents)
    })

print("NER extraction complete.")