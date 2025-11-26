import os
import json
from google.cloud import storage
from sklearn.model_selection import train_test_split

# =====================================================
# Config
# =====================================================

PROJECT_ID = os.getenv("GCP_PROJECT", "even-turbine-471117-u0")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "ac215-ml-workflow")

INPUT_GCS_PATH = "dnd-ml-dataset-raw/crd3_raw.jsonl"

OUTPUT_GCS_PREFIX = "dnd-ml-dataset-processor"
LOCAL_TEMP_DIR = "/persistent/processor_tmp"
LOCAL_INPUT_FILE = os.path.join(LOCAL_TEMP_DIR, "crd3_raw.jsonl")

# Optional subset mode for debugging small pipelines
SUBSET_SIZE = int(os.getenv("SUBSET_SIZE", "0"))  # 0 = disabled


# =====================================================
# Step 1: Download Raw Data
# =====================================================

def download_raw_data():
    print(f"📥 Downloading raw data from gs://{BUCKET_NAME}/{INPUT_GCS_PATH}...")
    os.makedirs(LOCAL_TEMP_DIR, exist_ok=True)

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(INPUT_GCS_PATH)
    blob.download_to_filename(LOCAL_INPUT_FILE)

    print(f"✅ Downloaded to {LOCAL_INPUT_FILE}")


# =====================================================
# Step 2: Clean + Split
# =====================================================

def clean_and_split():
    print("⚙️ Cleaning and Splitting data (80/10/10)...")

    valid_data = []

    with open(LOCAL_INPUT_FILE, "r") as f:
        for line in f:
            try:
                item = json.loads(line)

                response = item.get("response") or item.get("chunk")
                context = item.get("context", "Continue the D&D story and narrate what happens next:")

                if response and len(response.strip()) > 50:
                    valid_data.append({
                        "context": context,
                        "response": response
                    })

            except json.JSONDecodeError:
                continue

    print(f"   Total valid records after cleaning: {len(valid_data)}")

    # ------------------------------
    # SUBSET mode activated
    # ------------------------------
    if SUBSET_SIZE > 0:
        print(f"⚠️ SUBSET MODE ENABLED → Using only first {SUBSET_SIZE} samples")
        valid_data = valid_data[:SUBSET_SIZE]

    # Standard 80/10/10 split
    train_data, temp_data = train_test_split(valid_data, test_size=0.2, random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)

    print(f"   📊 Split Results:")
    print(f"      Train:      {len(train_data)}")
    print(f"      Validation: {len(val_data)}")
    print(f"      Test:       {len(test_data)}")

    return train_data, val_data, test_data


# =====================================================
# Step 3: Save + Upload (Gemini SFT Format)
# =====================================================

def save_and_upload(data, filename, limit=None):
    """
    Convert each record into Gemini SFT format and upload to GCS.
    Optional limit: For validation (max allowed = 5000; recommended = 256)
    """
    local_path = os.path.join(LOCAL_TEMP_DIR, filename)

    if limit is not None:
        data = data[:limit]

    with open(local_path, "w") as f:
        for item in data:
            output_line = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": item["context"]}]
                    },
                    {
                        "role": "model",
                        "parts": [{"text": item["response"]}]
                    }
                ]
            }
            f.write(json.dumps(output_line, ensure_ascii=False) + "\n")

    gcs_path = f"{OUTPUT_GCS_PREFIX}/{filename}"

    print(f"🚀 Uploading {filename} to gs://{BUCKET_NAME}/{gcs_path}...")

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":
    print("📦 Running Data Processor...")

    try:
        download_raw_data()

        train, val, test = clean_and_split()

        save_and_upload(train, "train.jsonl")
        save_and_upload(val, "validation.jsonl", limit=256)
        save_and_upload(test, "test.jsonl")

        print("\n🎉 Data Processing Complete!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
