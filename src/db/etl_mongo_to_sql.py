import psycopg2
import json
from pymongo import MongoClient

# -------------------------- 
# MongoDB setup 
# -------------------------- 
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["meetingbank"]
meetings_col = db["meetings"]
topics_col = db["nlp_topics"]
entities_col = db["nlp_entities"]
sentiment_col = db["nlp_sentiment"]

# -------------------------- 
# PostgreSQL setup 
# -------------------------- 
pg_conn = psycopg2.connect(
    host="localhost",
    dbname="nlp",
    user="postgres",
    password="admin" 
)
pg_cur = pg_conn.cursor()

# -------------------------- 
# Step 1: Load meetings_metadata 
# -------------------------- 
meeting_ids = []
for m in meetings_col.find({}):
    meeting_id = m["meeting_id"]
    city = m.get("city")
    num_turns = db.turns.count_documents({"meeting_id": meeting_id}) 
    entity_doc = entities_col.find_one({"meeting_id": meeting_id})
    num_entities = len(entity_doc["entities"]) if entity_doc else 0 
    sentiment_doc = sentiment_col.find_one({"meeting_id": meeting_id})
    avg_sentiment = sentiment_doc.get("avg_sentiment") if sentiment_doc else None

    pg_cur.execute(
        """ 
        INSERT INTO meetings_metadata 
        (meeting_id, city, num_turns, num_entities, avg_sentiment) 
        VALUES (%s, %s, %s, %s, %s) 
        ON CONFLICT (meeting_id) DO UPDATE 
        SET city=%s, num_turns=%s, num_entities=%s, avg_sentiment=%s 
        """,
        (meeting_id, city, num_turns, num_entities, avg_sentiment, city, num_turns, num_entities, avg_sentiment)
    )
    pg_conn.commit()
    meeting_ids.append(meeting_id)
print("✅ meetings_metadata populated.")

# -------------------------- 
# Step 2: Load NLP summary 
# -------------------------- 
for t in topics_col.find({}):
    meeting_id = t["meeting_id"]
    if meeting_id not in meeting_ids:
        continue
    dominant_topic = t["dominant_topic"]
    topic_keywords = t["topic_keywords"] 
    entity_doc = entities_col.find_one({"meeting_id": meeting_id})
    entities_json = entity_doc["entities"] if entity_doc else {} 
    sentiment_doc = sentiment_col.find_one({"meeting_id": meeting_id})
    avg_sentiment = sentiment_doc.get("avg_sentiment") if sentiment_doc else None

    pg_cur.execute(
        """ 
        INSERT INTO nlp_summary_by_meeting 
        (meeting_id, dominant_topic, topic_keywords, entities, avg_sentiment) 
        VALUES (%s, %s, %s, %s, %s) 
        ON CONFLICT (meeting_id) DO UPDATE 
        SET dominant_topic=%s, topic_keywords=%s, entities=%s, avg_sentiment=%s 
        """,
        (
            meeting_id, 
            dominant_topic, 
            topic_keywords, 
            json.dumps(entities_json),  
            avg_sentiment, 
            dominant_topic, 
            topic_keywords, 
            json.dumps(entities_json),  
            avg_sentiment
        )
    )
    pg_conn.commit()
pg_cur.close()
pg_conn.close()
print("✅ nlp_summary_by_meeting populated.")