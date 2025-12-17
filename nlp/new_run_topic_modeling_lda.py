from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from tqdm import tqdm
import numpy as np
import re

# ---------------------------
# MongoDB setup
# ---------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

turns_col = db["turns"]
meetings_col = db["meetings"]
topics_col = db["nlp_topics"]

# Clear previous topics
topics_col.delete_many({})

# ---------------------------
# HARD STOPWORDS (CRITICAL)
# ---------------------------
CUSTOM_STOPWORDS = {
    "thank", "thanks", "im", "ive", "youre", "dont", "didnt",
    "know", "think", "thinking", "just", "going", "want",
    "thats", "okay", "yes", "right", "like", "people",
    "time", "today", "meeting", "agenda", "item",
    "city", "council", "committee", "mayor", "chair"
}

ALL_STOPWORDS = list(ENGLISH_STOP_WORDS.union(CUSTOM_STOPWORDS))

# ---------------------------
# Text cleaner
# ---------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------------------------
# Step 1: Load + clean meetings
# ---------------------------
print("Loading meeting transcripts...")

meeting_texts = []
meeting_ids = []

meeting_docs = meetings_col.find({}, {"meeting_id": 1})

with tqdm(total=meetings_col.count_documents({}), unit="meetings") as pbar:
    for meeting_doc in meeting_docs:
        meeting_id = meeting_doc["meeting_id"]

        turns = turns_col.find(
            {"meeting_id": meeting_id},
            {"text": 1}
        )

        text = " ".join(t["text"] for t in turns if t.get("text"))
        text = clean_text(text)

        # DROP SHORT MEETINGS (ABSOLUTELY REQUIRED)
        if len(text.split()) < 120:
            pbar.update(1)
            continue

        meeting_texts.append(text)
        meeting_ids.append(meeting_id)
        pbar.update(1)

print(f"Loaded {len(meeting_texts)} cleaned meetings.")

# ---------------------------
# Step 2: Vectorization (THIS FIXES IT)
# ---------------------------
vectorizer = CountVectorizer(
    stop_words=ALL_STOPWORDS,
    max_df=0.6,          # 🔥 removes words in >60% of meetings
    min_df=2,
    max_features=4000,
    ngram_range=(1, 2)
)

doc_term_matrix = vectorizer.fit_transform(meeting_texts)

# ---------------------------
# Step 3: LDA
# ---------------------------
lda = LatentDirichletAllocation(
    n_components=6,
    random_state=42,
    learning_method="batch"
)

lda.fit(doc_term_matrix)

# ---------------------------
# Step 4: Store topics
# ---------------------------
feature_names = vectorizer.get_feature_names_out()

print("Storing topics in MongoDB...")
with tqdm(total=len(meeting_ids), unit="meetings") as pbar:
    for idx, meeting_id in enumerate(meeting_ids):
        topic_dist = lda.transform(doc_term_matrix[idx])
        dominant_topic = int(np.argmax(topic_dist))

        word_idx = lda.components_[dominant_topic].argsort()[-10:][::-1]
        keywords = [feature_names[i] for i in word_idx]

        topics_col.insert_one({
            "meeting_id": meeting_id,
            "dominant_topic": dominant_topic,
            "topic_keywords": keywords
        })

        pbar.update(1)

print("✅ LDA topic modeling FINALLY CLEAN.")