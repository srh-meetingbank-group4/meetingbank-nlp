import pandas as pd
from pathlib import Path

# Base project directory (meetingbank-nlp)
BASE_DIR = Path(__file__).resolve().parents[2]

# Raw and processed data paths
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load CSV files (RELATIVE PATHS)
train_data = pd.read_csv(RAW_DIR / "meetingbank_train.csv")
test_data = pd.read_csv(RAW_DIR / "meetingbank_test.csv")
val_data = pd.read_csv(RAW_DIR / "meetingbank_validation.csv")

# Basic validation
print("Train Data:")
print(train_data.shape)
print(train_data.columns, "\n")

print("Test Data:")
print(test_data.shape)
print(test_data.columns, "\n")

print("Validation Data:")
print(val_data.shape)
print(val_data.columns, "\n")

# Save to processed/
train_data.to_csv(PROCESSED_DIR / "meetingbank_train_processed.csv", index=False)
test_data.to_csv(PROCESSED_DIR / "meetingbank_test_processed.csv", index=False)
val_data.to_csv(PROCESSED_DIR / "meetingbank_validation_processed.csv", index=False)

print("✅ Processed datasets saved to data/processed/")