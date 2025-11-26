import os
import json
import time
from google import genai
from google.genai import types

# ==============================
# Configuration
# ==============================
# 🔴 核心修改：强制指向拥有配额的 Instructor Project ID
TARGET_PROJECT_ID = "542859696336"  # AC215 Instructor Project
TARGET_LOCATION = "us-central1"

# 你的个人 Bucket (确保 Service Account 对此 Bucket 有读取权限)
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "ac215-ml-workflow")

# 你的数据路径
TRAIN_URI = f"gs://{GCS_BUCKET_NAME}/dnd-ml-dataset-processor/train.jsonl"
VAL_URI = f"gs://{GCS_BUCKET_NAME}/dnd-ml-dataset-processor/validation.jsonl"

# ✅ 照抄你同学的作业：使用 Gemini 2.5 Flash
BASE_MODEL = "gemini-2.5-flash"

# 本地持久化目录
PERSIST_DIR = "/persistent"
os.makedirs(PERSIST_DIR, exist_ok=True)
JOB_INFO_FILE = os.path.join(PERSIST_DIR, "tuning_job.json")

# ==============================
# Initialize Gemini Client
# ==============================
print(f"🔌 Connecting to Instructor Project: {TARGET_PROJECT_ID}...")

# 在初始化时显式指定 Instructor Project ID
llm_client = genai.Client(
    vertexai=True,
    project=TARGET_PROJECT_ID,
    location=TARGET_LOCATION
)

# ============================================================
# Start a new fine-tuning job
# ============================================================
def start_tuning(epochs=3):
    print("\n=== Starting Gemini Supervised Fine-Tuning ===")
    print(f"Target Project: {TARGET_PROJECT_ID}")
    print(f"Base Model:     {BASE_MODEL}")
    print(f"Train Data:     {TRAIN_URI}")
    print(f"Epochs:         {epochs}")

    # 1. 定义数据集
    training_dataset = types.TuningDataset(gcs_uri=TRAIN_URI)
    validation_dataset = types.TuningDataset(gcs_uri=VAL_URI)

    # 2. 定义配置 (完全参考你同学的参数)
    tuning_config = types.CreateTuningJobConfig(
        epoch_count=epochs,
        learning_rate_multiplier=1.0, 
        adapter_size="ADAPTER_SIZE_FOUR",
        tuned_model_display_name="dnd-narrator-gemini25-student", # 改个名避免冲突
        validation_dataset=validation_dataset,
    )

    try:
        # 3. 提交任务
        job = llm_client.tunings.tune(
            base_model=BASE_MODEL,
            training_dataset=training_dataset,
            config=tuning_config,
        )
        
        print(f"✅ Job successfully submitted!")
        print(f"   Job Name: {job.name}")
        
        # 保存任务信息
        job_info = {
            "project_id": TARGET_PROJECT_ID,
            "job_name": job.name,
            "base_model": BASE_MODEL,
            "status": str(job.state),
            "start_time": time.time()
        }
        with open(JOB_INFO_FILE, "w") as f:
            json.dump(job_info, f, indent=2)

        return job.name

    except Exception as e:
        print(f"\n❌ FAILED to submit job to project {TARGET_PROJECT_ID}")
        print(f"Error details: {e}")
        # 如果这里报错 403，说明你的 Service Account 没被加进老师的项目
        raise e


# ============================================================
# Check tuning job status
# ============================================================
def check_status(job_name=None):
    if not os.path.exists(JOB_INFO_FILE):
        raise RuntimeError("No tuning_job.json found")

    with open(JOB_INFO_FILE) as f:
        info = json.load(f)

    job_name = job_name or info["job_name"]
    
    # 获取任务状态
    job = llm_client.tunings.get(name=job_name)

    print(f"\n📊 Job Status: {job.state}")
    
    # 更新本地记录
    info["status"] = str(job.state)
    
    # 如果任务完成，记录模型 Endpoint
    if job.tuned_model:
        print(f"🎉 Model Tuned! Endpoint: {job.tuned_model.endpoint}")
        info["tuned_model_endpoint"] = job.tuned_model.endpoint
        info["tuned_model_name"] = job.tuned_model.model

    with open(JOB_INFO_FILE, "w") as f:
        json.dump(info, f, indent=2)

    return job.state


# ============================================================
# Wait until training completes
# ============================================================
def wait_until_complete(job_name=None):
    print("=== Waiting for tuning job to complete ===")

    # 定义完成状态
    completed_states = {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "SUCCEEDED",
        "FAILED",
        "CANCELLED"
    }

    while True:
        try:
            state = check_status(job_name)
            if str(state) in completed_states:
                print(f"✓ Final state: {state}")
                return state
        except Exception as e:
            print(f"⚠️ Warning: Status check transient error: {e}")
        
        print("   Sleeping for 60s...")
        time.sleep(60)

# ============================================================
# Get the tuned model endpoint
# ============================================================
def get_tuned_model_name():
    if not os.path.exists(JOB_INFO_FILE):
        raise RuntimeError("No tuning job found.")

    with open(JOB_INFO_FILE) as f:
        info = json.load(f)

    if "tuned_model_endpoint" in info:
        return info["tuned_model_endpoint"]
    
    raise RuntimeError("Model fine-tuning not finished yet.")