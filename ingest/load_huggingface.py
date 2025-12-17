from datasets import load_dataset, concatenate_datasets
from pymongo import MongoClient
from tqdm import tqdm

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]

meetings_col = db["meetings"]
turns_col = db["turns"]

# Optional: clean collections before re-ingestion
# meetings_col.delete_many({})
# turns_col.delete_many({})

# Load HuggingFace MeetingBank dataset
train_ds = load_dataset("huuuyeah/meetingbank", split="train")
val_ds = load_dataset("huuuyeah/meetingbank", split="validation")
test_ds = load_dataset("huuuyeah/meetingbank", split="test")

dataset = concatenate_datasets([train_ds, val_ds, test_ds])

print("Keys in the dataset:")
print(dataset[0].keys())

loaded_meetings = set()
MAX_MEETINGS = 10  # limit for testing
skipped_meetings = 0
empty_transcripts = 0

print("Starting HuggingFace ingestion...")

for item in tqdm(dataset):
    meeting_id = item.get("id")          # Use 'id' as meeting_id
    transcript = item.get("transcript")
    summary = item.get("summary")
    city = None  # placeholder since not in HF dataset

    if meeting_id is None or transcript is None:
        skipped_meetings += 1
        continue

    # Convert transcript list to string if needed
    if isinstance(transcript, list):
        transcript_text = "\n".join([t for t in transcript if t.strip()])
    else:
        transcript_text = str(transcript).strip()

    if not transcript_text:
        empty_transcripts += 1
        continue

    # Insert meeting metadata
    if meeting_id not in loaded_meetings:
        if len(loaded_meetings) < MAX_MEETINGS:
            meetings_col.insert_one({
                "meeting_id": meeting_id,
                "city": city,
                "summary": summary
            })
            loaded_meetings.add(meeting_id)

            # Insert turns
            for idx, line in enumerate(transcript_text.split("\n")):
                if line.strip():
                    turns_col.insert_one({
                        "meeting_id": meeting_id,
                        "turn_id": idx + 1,
                        "text": line.strip()
                    })
        else:
            break

print(f"Ingested {len(loaded_meetings)} meetings successfully.")
print(f"Skipped {skipped_meetings} meetings due to missing data.")
print(f"Skipped {empty_transcripts} meetings due to empty transcripts.")