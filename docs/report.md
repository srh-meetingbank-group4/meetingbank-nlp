# MeetingBank Data Engineering Pipeline

## 1. Dataset Overview
Brief description of MeetingBank:
- Source (MeetingBank / HuggingFace / Zenodo)
- Modalities: text, audio, video
- Why it is unstructured / semi-structured

## 2. Data Ingestion
- CSV ingestion for transcripts
- MongoDB collections created:
  - meetings
  - turns
  - media
- Why MongoDB was chosen over relational DBs

## 3. Data Modeling
Explain schema design:
- meetings: metadata
- turns: transcript turns
- media: audio/video references
Explain why this separation is scalable.

## 4. Indexing Strategy
Explain:
- meeting_id index
- text index
Why indexing is critical for NLP-style queries.

## 5. Querying & Analytics
Describe:
- Keyword search ($text, regex)
- Aggregation pipelines
- Filtered analytics
Explain what each proves.

## 6. Query Efficiency
Explain:
- Explain plan
- Index usage
- Why this matters for large datasets

## 7. Architecture
Reference the flowchart diagram.

## 8. Conclusion
Summarize what the pipeline achieves and how it can be extended.