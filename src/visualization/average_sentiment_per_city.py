import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Create a database engine
engine = create_engine('postgresql://postgres:admin@localhost/meetingbank')

# SQL query
query = "SELECT city, AVG(avg_sentiment) AS avg_sentiment FROM nlp_sentiment_summary GROUP BY city;"

# Execute the query and store the result in a DataFrame
df = pd.read_sql(query, engine)

# Close the engine
engine.dispose()

# Create a bar plot
plt.figure(figsize=(8,5))
plt.bar(df['city'], df['avg_sentiment'], color='skyblue', edgecolor='black')
plt.title("Average Sentiment per City")
plt.xlabel("City")
plt.ylabel("Avg Sentiment")
plt.ylim(-1,1)
plt.tight_layout()
plt.show()