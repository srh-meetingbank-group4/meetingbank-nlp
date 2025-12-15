## Dataset Usage

This project uses the MeetingBank dataset, which provides multi-modal meeting data including transcripts, audio, video, and metadata.

- Transcripts were stored and analyzed using MongoDB aggregation pipelines for NLP-style preprocessing.
- Audio and video availability were modeled as metadata fields to demonstrate multi-modal data integration.
- MongoDB's flexible schema allowed handling meetings with partial or missing modalities without pipeline failure.
- Aggregations, text search, and indexed queries were used to demonstrate realistic data engineering workflows.

The dataset structure makes it suitable for large-scale unstructured and multi-modal analytics.