from bertopic import BERTopic
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from tqdm import tqdm

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]
turns_col = db["turns"]
topics_col = db["nlp_topics"]
meetings_col = db["meetings"]

# Clear previous topics
topics_col.delete_many({})

# Step 1: Prepare data
print("Loading meeting transcripts...")
meeting_texts = []
meeting_ids = []

meeting_docs = meetings_col.find({}, {"meeting_id": 1})
total_meetings = meetings_col.count_documents({})

with tqdm(total=total_meetings, unit="meetings") as pbar:
    for meeting_doc in meeting_docs:
        meeting_id = meeting_doc["meeting_id"]

        turns_cursor = turns_col.find(
            {"meeting_id": meeting_id},
            {"text": 1}
        )

        text = " ".join(t["text"] for t in turns_cursor if t.get("text"))

        if text.strip():
            meeting_texts.append(text)
            meeting_ids.append(meeting_id)

        pbar.update(1)

print(f"Loaded {len(meeting_texts)} meetings for topic modeling.")

# Step 2: BERTopic (MEMORY SAFE CONFIG)
vectorizer_model = CountVectorizer(
    stop_words="english",
    max_features=3000
)

topic_model = BERTopic(
    embedding_model="all-MiniLM-L6-v2",  # low memory
    vectorizer_model=vectorizer_model,
    min_topic_size=2,
    nr_topics=6,
    calculate_probabilities=False,
    verbose=True
)

# Step 3: Fit model
print("Fitting BERTopic model...")
topics, _ = topic_model.fit_transform(meeting_texts)

# Step 4: Store results
print("Storing topics in MongoDB...")
with tqdm(total=len(meeting_ids), unit="meetings") as pbar:
    for i, meeting_id in enumerate(meeting_ids):
        topic_id = int(topics[i])
        topic_info = topic_model.get_topic(topic_id)
        keywords = [word for word, _ in topic_info] if topic_info else []

        topics_col.insert_one({
            "meeting_id": meeting_id,
            "dominant_topic": topic_id,
            "topic_keywords": keywords
        })

        pbar.update(1)

print("✅ Topic modeling complete.")