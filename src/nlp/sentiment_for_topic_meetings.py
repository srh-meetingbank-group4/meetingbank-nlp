import psycopg2
from transformers import pipeline
import numpy as np

# -----------------------------
# DB CONNECTION
# -----------------------------
conn = psycopg2.connect(
    host="localhost",
    database="meetingbank",
    user="postgres",
    password="admin"
)
cur = conn.cursor()

# -----------------------------
# Load meetings with topics
# -----------------------------
cur.execute("""
    SELECT DISTINCT meeting_id FROM nlp_topics
""")
meeting_ids = [row[0] for row in cur.fetchall()]
print("Meetings to process:", meeting_ids)

# -----------------------------
# Load sentiment model
# -----------------------------
sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# -----------------------------
# Process each meeting
# -----------------------------
for meeting_id in meeting_ids:
    cur.execute("""
        SELECT t.turn_text 
        FROM turns t 
        JOIN agenda_items a ON t.agenda_id = a.agenda_id 
        WHERE a.meeting_id = %s AND t.turn_text IS NOT NULL AND LENGTH(t.turn_text) > 20 
        LIMIT 200
    """, (meeting_id,))
    texts = [row[0] for row in cur.fetchall()]
    if not texts:
        continue
    results = sentiment_model(texts)
    scores = []
    positives = 0
    negatives = 0
    for r in results:
        score = r["score"]
        if r["label"] == "POSITIVE":
            scores.append(score)
            positives += 1
        else:
            scores.append(-score)
            negatives += 1
    avg_sentiment = float(np.mean(scores))
    positive_ratio = positives / len(scores)
    negative_ratio = negatives / len(scores)
    
    # Get city
    cur.execute("SELECT city FROM nlp_meetings WHERE id = %s", (meeting_id,))
    city = cur.fetchone()[0]
    cur.execute("""
        INSERT INTO nlp_sentiment_summary 
        (meeting_id, city, avg_sentiment, positive_ratio, negative_ratio, model)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        meeting_id,
        city,
        avg_sentiment,
        positive_ratio,
        negative_ratio,
        "distilbert-base-uncased-finetuned-sst-2-english"
    ))
    print(f"Inserted sentiment for meeting {meeting_id}")
conn.commit()
cur.close()
conn.close()
print("✅ Sentiment recomputed for topic meetings")