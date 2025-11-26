# Data Versioning

## Overview

This module implements a complete data versioning and reproducibility workflow using:

DVC (Data Version Control) — diff-based versioning for large datasets

Google Cloud Storage (GCS) — remote artifact store

Git — versioning for metadata (data.dvc)

Docker — isolated, reproducible execution environment

This system is responsible for tracking two key layers of text data used in our fine-tuning workflow:

```
data/
├── raw/        # unprocessed, collector-produced data
└── processed/  # cleaned + normalized data for training
```


Both layers are version-controlled by DVC, and all binary artifacts are stored remotely in: GCS bucket: gs://dnd-data-versioning/dvc_store

## Why DVC (Justification Based on Data Characteristics)

Our dataset is static in the sense that the raw source text does not change over time.
However, the fine-tuning workflow is version-sensitive: updates to preprocessing logic, filtering rules, or training configurations require strict dataset versioning to ensure reproducibility.
Therefore, even though the raw data is static, we use DVC to track the exact version of raw/ and processed/ used for each fine-tuning experiment.

## How This Supports Fine-Tuning MLOps

1. Traceability

We link:

```
dataset_v3 → processed_v3 → training_run_17 → model_v17
```

2. Reproducibility across environments

Training may occur on:

Local Docker
GCP VM
Vertex AI

All must restore the exact dataset with:
```
dvc pull
```


## Folder Structure

We intentionally exclude training_splits/ because those belong to the training module, not DV.
```
src/data-versioning/
│
├── data/
│   ├── raw/         # raw collected data
│   └── processed/   # normalized data
│
├── data.dvc         # DVC metadata (hash, size, pointer)
├── .dvc/            # DVC internal cache structure
│
├── Dockerfile
├── docker-shell.sh
├── docker-entrypoint.sh
├── pyproject.toml
├── uv.lock
└── README.md        ← this file
```
## Versioning Workflow

1. Initialize and track data folder
```
dvc init
dvc add data
git add data.dvc .dvc/config
git commit -m "Initialize DVC tracking"
```

2. Push dataset to remote storage
```
dvc push
```

3. Modify raw → processed and update version
```
dvc add data
git commit -am "Update dataset vX"
dvc push
```

## Change Detection (for MLOps)

DVC detects when raw data changes:
```
dvc status
```

Typical output:
```
data.dvc:
    changed hash
```

## Automated Testing

We implemented a DV test suite (test_data_versioning.py):

| Test                                    | Purpose                                |
| --------------------------------------- | -------------------------------------- |
| `test_01_raw_folder_exists`             | Ensures directory structure is valid   |
| `test_02_dvc_add_data_folder`           | Verifies metadata creation             |
| `test_03_dvc_push_and_pull`             | Ensures remote storage + recovery work |
| `test_04_hash_changes_when_raw_changes` | Ensures DVC detects data changes       |

All tests pass inside the DV Docker container, confirming that the versioning workflow is correct, deterministic, and reproducible.