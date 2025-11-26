import os
import subprocess
from typing import List

# ============================================================
# Environment / Config
# ============================================================

# GCP settings (must be set correctly in your shell)
GCP_PROJECT = os.getenv("GCP_PROJECT", "even-turbine-471117-u0")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "ac215-ml-workflow")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Service account inside the containers
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/secrets/llm-service-account.json",
)

SECRETS_DIR = os.getenv("SECRETS_DIR", os.path.expanduser("~/Desktop/AC215_The_Bear_Dungeon/secrets"))
PERSIST_DIR = os.getenv("PERSIST_DIR", os.path.expanduser("~/Desktop/AC215_The_Bear_Dungeon/src/ml-workflow/persistent"))

# Docker images
COLLECTOR_IMAGE = os.getenv("COLLECTOR_IMAGE", "data-collector")
PROCESSOR_IMAGE = os.getenv("PROCESSOR_IMAGE", "dnd-processor")
TRAINER_IMAGE = os.getenv("TRAINER_IMAGE", "dnd-trainer")


# ============================================================
# Utility: run docker command
# ============================================================

def _run(cmd_list: List[str]) -> None:
    print("\n============================================")
    print("Running command:")
    print(" ".join(cmd_list))
    print("============================================\n")

    result = subprocess.run(cmd_list)
    if result.returncode != 0:
        raise RuntimeError(f"Docker command failed with code {result.returncode}")


def _base_docker_args() -> list:
    """
    Common env + volume mounts used by all pipeline containers.
    """
    return [
        "docker", "run", "--rm",
        "-e", f"GCP_PROJECT={GCP_PROJECT}",
        "-e", f"GCS_BUCKET_NAME={GCS_BUCKET_NAME}",
        "-e", f"GCP_LOCATION={GCP_LOCATION}",
        "-e", f"GOOGLE_APPLICATION_CREDENTIALS={GOOGLE_APPLICATION_CREDENTIALS}",
        "-v", f"{SECRETS_DIR}:/secrets",
        "-v", f"{PERSIST_DIR}:/persistent",
    ]


# ============================================================
# 1️⃣ Collector
# ============================================================

def run_collector() -> None:
    """
    Launches `data-collector` container to download CRD3 and upload raw JSONL
    into:
        gs://<bucket>/dnd-ml-dataset-raw/crd3_raw.jsonl

    The collector image itself already knows this path.
    """
    cmd = _base_docker_args() + [COLLECTOR_IMAGE]
    _run(cmd)


# ============================================================
# 2️⃣ Processor
# ============================================================

def run_processor() -> None:
    """
    Launches `dnd-processor` container to:
        - download raw crd3_raw.jsonl from your bucket
        - clean + split (80/10/10)
        - convert to Gemini SFT `contents` schema
        - limit validation to 256 samples
        - upload train/validation/test.jsonl back to GCS:
              gs://<bucket>/dnd-ml-dataset-processor/
    """
    cmd = _base_docker_args() + [PROCESSOR_IMAGE]
    _run(cmd)


# ============================================================
# 3️⃣ Trainer (Gemini Fine-Tuning)
# ============================================================

def run_trainer(epochs: int = 1) -> None:
    """
    Launches `dnd-trainer` container to start supervised fine-tuning.

    It expects:
        GCP_PROJECT, GCS_BUCKET_NAME, GCP_LOCATION, GOOGLE_APPLICATION_CREDENTIALS
        train/validation.jsonl present in your bucket under
            dnd-ml-dataset-processor/
    """
    cmd = _base_docker_args() + [
        TRAINER_IMAGE,
        "tune",
        "--epochs", str(epochs),
    ]
    _run(cmd)


# ============================================================
# 4️⃣ Full pipeline
# ============================================================

def run_all(epochs: int = 1) -> None:
    """
    Run the full pipeline end-to-end:

        1. data-collector
        2. dnd-processor
        3. dnd-trainer (fine-tuning)

    If any step fails, the pipeline aborts.
    """
    print("\n============================================")
    print("🚀 STARTING FULL DnD MLOPS PIPELINE")
    print("============================================")

    run_collector()
    run_processor()
    run_trainer(epochs=epochs)

    print("\n============================================")
    print("!PIPELINE COMPLETED! (collector → processor → trainer)")
    print("============================================")


print("model.py loaded: clean container-oriented workflow is ready.")
