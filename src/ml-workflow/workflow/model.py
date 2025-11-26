import os
import subprocess
from typing import List

# ============================================================
# Environment / Config (Host Paths mailed from docker-shell.sh)
# ============================================================

GCP_PROJECT = os.getenv("GCP_PROJECT", "even-turbine-471117-u0")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "ac215-ml-workflow")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Inside ALL child containers, creds path is always /secrets/llm-service-account.json
GOOGLE_APPLICATION_CREDENTIALS = "/secrets/llm-service-account.json"

# ------------------------------------------------------------
# Host paths (critical for Docker-out-of-Docker)
# These MUST come from docker-shell.sh
# ------------------------------------------------------------
MOUNT_CONFIGS_DIR = os.getenv("MOUNT_CONFIGS_DIR")
MOUNT_SECRETS_DIR = os.getenv("MOUNT_SECRETS_DIR")
MOUNT_PERSIST_DIR = os.getenv("MOUNT_PERSIST_DIR")

if not MOUNT_CONFIGS_DIR or not MOUNT_SECRETS_DIR or not MOUNT_PERSIST_DIR:
    raise RuntimeError("Host mount dirs (MOUNT_* vars) were not provided! Fix docker-shell.sh.")

# ------------------------------------------------------------
# Images
# ------------------------------------------------------------
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


# ============================================================
# Build child container docker run base arguments
# ============================================================

def _base_docker_args() -> list:
    """
    Common settings for all children containers
    """
    return [
        "docker", "run", "--rm",

        # env vars
        "-e", f"GCP_PROJECT={GCP_PROJECT}",
        "-e", f"GCS_BUCKET_NAME={GCS_BUCKET_NAME}",
        "-e", f"GCP_LOCATION={GCP_LOCATION}",
        "-e", f"GOOGLE_APPLICATION_CREDENTIALS={GOOGLE_APPLICATION_CREDENTIALS}",

        # MLOps critical mounts (host paths → child container)
        "-v", f"{MOUNT_SECRETS_DIR}:/secrets",
        "-v", f"{MOUNT_PERSIST_DIR}:/persistent",
        "-v", f"{MOUNT_CONFIGS_DIR}:/app/configs",
    ]


# ============================================================
# 1️⃣ Collector
# ============================================================

def run_collector() -> None:
    cmd = _base_docker_args() + [COLLECTOR_IMAGE]
    _run(cmd)


# ============================================================
# 2️⃣ Processor
# ============================================================

def run_processor() -> None:
    cmd = (
        _base_docker_args()
        + [
            "-e", "PROCESSOR_CONFIG_PATH=/app/configs/processor_config.yaml",
            PROCESSOR_IMAGE,
            "python", "processor.py",
        ]
    )
    _run(cmd)


# ============================================================
# 3️⃣ Trainer (Gemini Fine-Tuning)
# ============================================================

def run_trainer(epochs: int = 1) -> None:
    """
    Launches dnd-trainer, injects configuration path, and runs supervised fine-tuning.
    """

    # Inject config into trainer container
    config_injection = [
        "-e", "TRAINING_CONFIG_PATH=/app/configs/training_config.yaml"
    ]

    # Use host paths for all mounts
    base = [
        "docker", "run", "--rm",
        "--entrypoint", "python",            
        "-e", f"GCP_PROJECT={GCP_PROJECT}",
        "-e", f"GCS_BUCKET_NAME={GCS_BUCKET_NAME}",
        "-e", f"GCP_LOCATION={GCP_LOCATION}",
        "-e", "GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json",
        "-v", f"{MOUNT_SECRETS_DIR}:/secrets",
        "-v", f"{MOUNT_PERSIST_DIR}:/persistent",
        "-v", f"{MOUNT_CONFIGS_DIR}:/app/configs",
    ]

    # Explicit python command executed inside trainer container
    script_command = [
        "dnd-trainer",              # image name
        "-m", "trainer.task",       # run trainer/task.py as module
        "tune",
        "--epochs", str(epochs),
    ]

    cmd = base + config_injection + script_command
    _run(cmd)



# ============================================================
# 4️⃣ Full pipeline
# ============================================================

def run_all(epochs: int = 1) -> None:
    print("\n============================================")
    print("🚀 STARTING FULL DnD MLOPS PIPELINE")
    print("============================================")

    run_processor()
    run_trainer(epochs=epochs)

    print("\n============================================")
    print("🌟 PIPELINE COMPLETED! (processor → trainer)")
    print("============================================")


print("model.py loaded: clean container-oriented workflow is ready.")
