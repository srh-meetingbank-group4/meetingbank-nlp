# meetingbank-nlp
Group 4 — MeetingBank ETL + NLP pipeline for Data Engineering module

# MeetingBank NLP Pipeline
### Group 4 — ETL & NLP Pipeline for City Council Meeting Analysis
## 📌 Project Overview
City council meetings generate large volumes of semi-structured textual data. This project implements an end-to-end data engineering pipeline on a subset of the MeetingBank dataset, transforming raw meeting data into a structured, queryable system. We extract insights like meeting-level sentiment, dominant topics, named entities, and city-level trends.

## 🗂 Dataset
- **Source:** MeetingBank (Hu et al., ACL 2023)
- **Content:** City council meeting transcripts, agenda items, and metadata
- **Scope:** 13 meetings, cities include Seattle, Boston, Denver

## 🏗 System Architecture
MeetingBank Dataset → Data Ingestion (Python) → Data Cleaning → NLP Processing → Hybrid Storage (PostgreSQL + MongoDB)

## 🔄 Pipeline Components
1. **Data Ingestion**: Parsed MeetingBank CSV and JSON transcripts
2. **Data Cleaning**: Removed nulls, standardized names
3. **NLP Processing**: NER (spaCy), Sentiment (DistilBERT), Topic Modeling (LDA)
4. **Storage**: PostgreSQL (structured) + MongoDB (unstructured)
5. **Analysis**: SQL queries for sentiment, entities, topics

## 🧠 Technologies Used
- Python, PostgreSQL, MongoDB, HuggingFace, spaCy, Gensim, Pandas

## 📊 Example Analyses
- City-wise sentiment comparison
- Top entities per city
- Topic distribution

## ⚖ Ethics & Responsible Use
- Public governance data, no personal profiling
- NLP for academic analysis only

## 🚀 Future Enhancements
- Automate pipeline (Airflow)
- Scale to full MeetingBank dataset
- Cloud deployment

## 📚 References
Hu, Y., et al. MeetingBank: A Benchmark Dataset for Meeting Understanding, ACL 2023.

## 📎 Repository Structure
meetingbank-nlp/
├── src/
├── notebooks/
├── sql/
├── visualizations/
└── README.md