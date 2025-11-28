import os
import json
import time
from google import genai
from google.genai import types

PERSIST_DIR = "/persistent/training_runs"
os.makedirs(PERSIST_DIR, exist_ok=True)
JOB_INFO_FILE = os.path.join(PERSIST_DIR, "last_tuning_job.json")

# ============================================================
# Start a new fine-tuning job
# ============================================================
def start_tuning(
    project_id,           
    location,             # us-central1
    base_model,           # gemini-2.5-flash
    tuned_model_display_name,
    train_dataset_uri,    # 
    validation_dataset_uri,
    epochs=3,
    adapter_size=4,
    learning_rate_multiplier=1.0
):
    print("\n=== Starting Gemini Supervised Fine-Tuning (SDK: google-genai) ===")
    print(f"🔌 Target Project: {project_id}")
    print(f"🤖 Base Model:     {base_model}")
    print(f"📂 Train Data:     {train_dataset_uri}")
    
    # 1. Initialize Client 
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )


    train_ds = types.TuningDataset(gcs_uri=train_dataset_uri)
    val_ds = types.TuningDataset(gcs_uri=validation_dataset_uri)


    adapter_enum = "ADAPTER_SIZE_FOUR"
    if adapter_size == 1: adapter_enum = "ADAPTER_SIZE_ONE"
    elif adapter_size == 8: adapter_enum = "ADAPTER_SIZE_EIGHT"
    elif adapter_size == 16: adapter_enum = "ADAPTER_SIZE_SIXTEEN"


    timestamp = int(time.time())
    unique_display_name = f"{tuned_model_display_name}-{timestamp}"


    tuning_config = types.CreateTuningJobConfig(
        epoch_count=epochs,
        learning_rate_multiplier=learning_rate_multiplier,
        adapter_size=adapter_enum,
        tuned_model_display_name=unique_display_name,
        validation_dataset=val_ds,
    )

    try:

        print("🚀 Submitting job to Vertex AI...")
        job = client.tunings.tune(
            base_model=base_model,
            training_dataset=train_ds,
            config=tuning_config,
        )
        
        print(f"✅ Job successfully submitted!")
        print(f"   Job Resource Name: {job.name}")
        

        job_info = {
            "project_id": project_id,
            "location": location,
            "job_name": job.name,
            "base_model": base_model,
            "status": str(job.state),
            "start_time": time.time()
        }
        with open(JOB_INFO_FILE, "w") as f:
            json.dump(job_info, f, indent=2)

        return job.name

    except Exception as e:
        print(f"\n❌ FAILED to submit job to project {project_id}")
        print(f"Error details: {e}")
        raise e

# ============================================================
# Check Status
# ============================================================
def check_status():
    if not os.path.exists(JOB_INFO_FILE):
        return "No local job history found."

    with open(JOB_INFO_FILE) as f:
        info = json.load(f)
    
    job_name = info["job_name"]
    project_id = info["project_id"]
    location = info["location"]

    # Re-init client to check status
    client = genai.Client(vertexai=True, project=project_id, location=location)
    job = client.tunings.get(name=job_name)
    
    print(f"\n📊 Job Status: {job.state}")
    
    info["status"] = str(job.state)
    if job.tuned_model:
         print(f"🎉 Model Tuned! Endpoint: {job.tuned_model.endpoint}")
         info["tuned_model_endpoint"] = job.tuned_model.endpoint
    
    with open(JOB_INFO_FILE, "w") as f:
        json.dump(info, f, indent=2)

    return str(job.state)

# ============================================================
# Wait Loop
# ============================================================
def wait_until_complete():
    print("=== Waiting for tuning job to complete ===")
    
    while True:
        try:
            state = check_status()
            if state in ["JOB_STATE_SUCCEEDED", "SUCCEEDED", "JOB_STATE_FAILED", "FAILED", "JOB_STATE_CANCELLED"]:
                print(f"✓ Final state: {state}")
                return state
        except Exception as e:
            print(f"⚠️ Check error: {e}")
        
        print("   Sleeping for 60s...")
        time.sleep(60)

# ============================================================
# Get Model
# ============================================================
def get_tuned_model_name():
    if not os.path.exists(JOB_INFO_FILE):
        return "No job history."
    with open(JOB_INFO_FILE) as f:
        info = json.load(f)
    return info.get("tuned_model_endpoint", "Job not finished yet.")