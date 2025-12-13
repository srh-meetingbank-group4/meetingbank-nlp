import pandas as pd
import re
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
INPUT_FILES = {
    "train": "meetingbank_train.csv",
    "test": "meetingbank_test.csv",
    "validation": "meetingbank_validation.csv",
}
OUTPUT_SUFFIX = "_cleaned"

print("Script is running...")

def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)  # normalize whitespace
    text = re.sub(r"[^\w\s.,!?]", "", text)  # remove junk symbols
    return text.strip()

def add_features(df):
    df["transcript_word_count"] = df["transcript"].apply(lambda x: len(x.split()))
    df["summary_word_count"] = df["summary"].apply(lambda x: len(x.split()))
    df["transcript_char_count"] = df["transcript"].apply(len)
    return df

def process_file(filename):
    input_path = RAW_DIR / filename
    print(f"Processing file: {input_path}")

    df = pd.read_csv(input_path)

    df["summary"] = df["summary"].apply(clean_text)
    df["transcript"] = df["transcript"].apply(clean_text)

    df = add_features(df)

    output_path = PROCESSED_DIR / filename.replace(".csv", f"{OUTPUT_SUFFIX}.csv")
    df.to_csv(output_path, index=False)

    print(f"✅ Saved: {output_path.name}")


if __name__ == "__main__":
    try:
        for split, file in INPUT_FILES.items():
            process_file(file)
        print("✅ Cleaning + feature engineering complete.")
    except Exception as e:
        print(f"Error: {e}")