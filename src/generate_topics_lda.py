# generate_topics_lda.py
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import psycopg2
from sqlalchemy import create_engine

# -----------------------------
# 1️⃣ Connect to PostgreSQL
# -----------------------------
engine = create_engine('postgresql://postgres:admin@localhost/meetingbank')
conn = psycopg2.connect(
    host="localhost",
    database="meetingbank",
    user="postgres",
    password="admin"
)
cur = conn.cursor()

# -----------------------------
# 2️⃣ Load meeting agendas
# -----------------------------
df = pd.read_sql("SELECT meeting_id, city, agenda FROM nlp_meetings WHERE agenda IS NOT NULL;", engine)

# -----------------------------
# 3️⃣ Text vectorization
# -----------------------------
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['agenda'])

# -----------------------------
# 4️⃣ Fit LDA model
# -----------------------------
n_topics = 6  # you can change to 5-8
lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(X)

# -----------------------------
# 5️⃣ Assign dominant topic per meeting
# -----------------------------
topic_results = []
feature_names = vectorizer.get_feature_names_out()
for i, topic_dist in enumerate(lda.transform(X)):
    dominant_topic = topic_dist.argmax()
    keywords = ", ".join([feature_names[j] for j in lda.components_[dominant_topic].argsort()[-5:]])
    topic_results.append((int(df.iloc[i]['meeting_id']), df.iloc[i]['city'], int(dominant_topic), f"Topic {dominant_topic}", keywords))

# -----------------------------
# 6️⃣ Insert into PostgreSQL
# -----------------------------
for r in topic_results:
    cur.execute("""
        INSERT INTO nlp_topics(meeting_id, city, dominant_topic, topic_label, keywords)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (meeting_id) DO NOTHING;
    """, r)

conn.commit()
cur.close()
conn.close()
print("✅ LDA topics generated and inserted into PostgreSQL!")