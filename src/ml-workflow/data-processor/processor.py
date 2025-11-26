import os
import json
import yaml
from pathlib import Path
from google.cloud import storage
from sklearn.model_selection import train_test_split

# =====================================================
# Utility: Parse GCS URI
# =====================================================

def parse_gs_uri(uri: str):
    """
    Parses a gs:// URI into (bucket, object_path)
    Example:
        "gs://ac215-ml-workflow/dnd-ml-dataset-raw/crd3_raw.jsonl"
        → ("ac215-ml-workflow", "dnd-ml-dataset-raw/crd3_raw.jsonl")
    """
    assert uri.startswith("gs://"), f"Invalid GCS URI: {uri}"
    path = uri[5:]  # strip "gs://"
    bucket, object_path = path.split("/", 1)
    return bucket, object_path


# =====================================================
# Load YAML config
# =====================================================

DEFAULT_CONFIG_PATH = "/app/configs/processor_config.yaml"
CONFIG_PATH = os.getenv("PROCESSOR_CONFIG_PATH", DEFAULT_CONFIG_PATH)

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

dataset_cfg = cfg["dataset"]
schema_cfg = cfg["schema"]
version_cfg = cfg["version"]


# =====================================================
# Resolve config values
# =====================================================

PROJECT_ID = os.getenv("GCP_PROJECT", "even-turbine-471117-u0")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "ac215-ml-workflow")

RAW_URI = dataset_cfg["raw_uri"]     # e.g., gs://ac215-ml-workflow/dnd-ml-dataset-raw/crd3_raw.jsonl
OUTPUT_URI = dataset_cfg["output_uri"]
SUBSET_SIZE = int(os.getenv("SUBSET_SIZE", dataset_cfg["subset_size"]))
TRAIN_SPLIT = dataset_cfg["train_split"]

PROCESSOR_VERSION = version_cfg["processor_version"]
SCHEMA_VERSION = version_cfg["schema_version"]

INPUT_FIELDS = schema_cfg["input_fields"]
OUTPUT_FIELDS = schema_cfg["output_fields"]

LOCAL_TEMP_DIR = "/persistent/processor_tmp"
LOCAL_INPUT_FILE = os.path.join(LOCAL_TEMP_DIR, "input.jsonl")  # fixed local filename

# parse raw and output locations
RAW_BUCKET, RAW_OBJECT = parse_gs_uri(RAW_URI)
OUTPUT_BUCKET, OUTPUT_PREFIX = parse_gs_uri(OUTPUT_URI)


# =====================================================
# Step 1: Download Raw Data
# =====================================================

def download_raw_data():
    print(f"📥 Downloading raw data from {RAW_URI} ...")
    os.makedirs(LOCAL_TEMP_DIR, exist_ok=True)

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(RAW_BUCKET)

    blob = bucket.blob(RAW_OBJECT)
    if not blob.exists():
        raise RuntimeError(f"ERROR: Raw dataset not found: {RAW_URI}")

    blob.download_to_filename(LOCAL_INPUT_FILE)

    print(f"✅ Downloaded to: {LOCAL_INPUT_FILE}")
    return LOCAL_INPUT_FILE


# =====================================================
# Step 2: Clean + Split
# =====================================================

def clean_and_split(input_path):
    print(f"⚙️ Cleaning and splitting data using TRAIN_SPLIT={TRAIN_SPLIT}")

    valid_data = []

    with open(input_path, "r") as f:
        for line in f:
            try:
                item = json.loads(line)

                context = item.get("context") or "Continue the D&D story:"
                response = item.get("response") or item.get("chunk")

                if response and len(response.strip()) > 50:
                    valid_data.append({"context": context, "response": response})

            except json.JSONDecodeError:
                continue

    print(f"   Total valid rows: {len(valid_data)}")

    if SUBSET_SIZE > 0:
        print(f"⚠️ SUBSET MODE → Using first {SUBSET_SIZE} samples")
        valid_data = valid_data[:SUBSET_SIZE]

    if len(valid_data) == 0:
        raise RuntimeError("Valid_data is empty. Check raw file content.")

    train_data, val_test = train_test_split(valid_data, test_size=1-TRAIN_SPLIT, random_state=42)
    val_data, test_data = train_test_split(val_test, test_size=0.5, random_state=42)

    print(f"📊 Split results:")
    print(f"   Train:      {len(train_data)}")
    print(f"   Validation: {len(val_data)}")
    print(f"   Test:       {len(test_data)}")

    return train_data, val_data, test_data


# =====================================================
# Step 3: Save + Upload
# =====================================================

def save_and_upload(data, filename, limit=None):
    """
    Convert each record into Gemini SFT format and upload to GCS.
    Optional limit: For validation (max allowed = 5000; recommended = 256)
    """

    # Local temporary output path
    local_path = os.path.join(LOCAL_TEMP_DIR, filename)

    # Apply subset limit
    if limit is not None:
        data = data[:limit]

    # ---- Write Gemini SFT format ----
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

    # ---- Build correct GCS output path ----
    normalized_prefix = OUTPUT_PREFIX.rstrip("/")  # avoid //
    versioned_path = f"{normalized_prefix}/{PROCESSOR_VERSION}/{filename}"

    print(f"🚀 Uploading {filename} → gs://{OUTPUT_BUCKET}/{versioned_path}...")

    # Upload
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(OUTPUT_BUCKET)
    blob = bucket.blob(versioned_path)

    blob.upload_from_filename(local_path)


# =====================================================
# Step 4: Save Config Snapshot (Versioned)
# =====================================================

def save_config_snapshot():
    """
    Saves a snapshot of the YAML config used by this processor run,
    and uploads it to GCS alongside the versioned processor output.
    
    Example GCS path:
    gs://<bucket>/<output_prefix>/<processor_version>/config.yaml
    """

    local_snapshot_dir = os.path.join(LOCAL_TEMP_DIR, "config_snapshot")
    os.makedirs(local_snapshot_dir, exist_ok=True)

    local_snapshot_path = os.path.join(local_snapshot_dir, "config.yaml")

    # ---- Save local snapshot ----
    with open(CONFIG_PATH, "r") as src:
        with open(local_snapshot_path, "w") as dst:
            dst.write(src.read())

    # ---- Build versioned GCS path ----
    normalized_prefix = OUTPUT_PREFIX.rstrip("/")
    versioned_config_path = f"{normalized_prefix}/{PROCESSOR_VERSION}/config.yaml"

    print(f"📝 Saving config snapshot → gs://{OUTPUT_BUCKET}/{versioned_config_path}")

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(OUTPUT_BUCKET)
    blob = bucket.blob(versioned_config_path)

    blob.upload_from_filename(local_snapshot_path)

    print("✅ Config snapshot uploaded.")



# =====================================================
# Main
# =====================================================

if __name__ == "__main__":
    print("📦 Running Data Processor with full YAML config...")

    try:
        input_path = download_raw_data()

        train, val, test = clean_and_split(input_path)

        save_and_upload(train, "train.jsonl")
        save_and_upload(val, "validation.jsonl", limit=256)
        save_and_upload(test, "test.jsonl")
        save_config_snapshot()
        print("\n🎉 Data Processing Complete!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
