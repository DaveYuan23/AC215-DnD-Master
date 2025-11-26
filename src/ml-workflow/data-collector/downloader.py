import os
import json
import glob
from google.cloud import storage
from datasets import load_dataset

# ========== Config ==========
OUTPUT_FOLDER = "downloaded_data"
OUTPUT_FILENAME = "crd3_raw.jsonl"

TARGET_BUCKET = os.getenv("GCS_BUCKET_NAME", "ac215-ml-workflow")
TARGET_PREFIX = "dnd-ml-dataset-raw"
PROJECT_ID = os.getenv("GCP_PROJECT", "even-turbine-471117-u0")


def load_crd3():

    print("📥 Loading CRD3 dataset from HuggingFace...")
    dataset = load_dataset("microsoft/crd3", trust_remote_code=True)
    print("✅ CRD3 dataset loaded.")
    return dataset


def process_and_save(dataset):

    print("⚙️ Processing data ...")
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    local_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)

    FIXED_CONTEXT = "Continue the D&D story and narrate what happens next:"
    
    total_count = 0

    with open(local_path, "w") as f:
        for split in ['train', 'validation', 'test']:
            if split in dataset:
                print(f"   Processing split: {split}...")
                
                for item in dataset[split]:
                    chunk = item.get("chunk", "")
                    
                    if chunk and len(chunk.strip()) > 50:
                        
                        record = {
                            "context": FIXED_CONTEXT,
                            "response": chunk,
                            "original_split": split 
                        }
                        
                        f.write(json.dumps(record) + "\n")
                        total_count += 1

    print(f"✅ Processed & Saved {total_count} records to {local_path}")
    return local_path


def upload_to_gcs(local_path):

    print("🚀 Uploading to GCS...")

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(TARGET_BUCKET)

    dest_path = f"{TARGET_PREFIX}/{OUTPUT_FILENAME}"
    blob = bucket.blob(dest_path)

    blob.upload_from_filename(local_path)

    print(f"✅ Uploaded successfully!")
    print(f"   Remote: gs://{TARGET_BUCKET}/{dest_path}")


if __name__ == "__main__":
    print("📦 Running CRD3 Data Collector (With Pre-processing)...")

    try:

        ds = load_crd3()

        file_path = process_and_save(ds)

        upload_to_gcs(file_path)

        print("\n🎉 COMPLETE")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()