# Data Versioning for AC215 Milestone 4  
**System: DVC + GCS + Git + Dockerized CLI**

---

## Overview

This module implements a complete **data-versioning system** for the Milestone 4 fine-tuning workflow.  
We manage **three layers of textual data**, all of which are version-controlled using **DVC (Data Version Control)**:

"""
data/
│
├── raw/ # Source data (not cleaned)
├── processed/ # Normalized + cleaned text
└── training_splits/ # train/val/test JSONL for fine-tuning

"""


All **binary data + large files** (the real dataset contents) are stored in: GCS bucket: gs://dnd-data-versioning/dvc_store


All **DVC metadata** (data pointers, version hashes) are stored in Git and synced to: GitHub repo: DaveYuan23/AC215_The_Bear_Dungeon (branch: milestone4-yizhen)

## How This Supports Fine-Tuning MLOps

Fine-tuning workflows depend on three guarantees:

Deterministic dataset

Traceability of which dataset produced which model

Ability to rollback / experiment with multiple data revisions

With this versioning system:

A fine-tuning pipeline can checkout dataset_vX

Perform preprocessing / tokenization

Train model

Produce a model artifact tagged consistently (e.g., ft_vX)


## Folder Structure
"""
milestone4/
│
└── data-versioning/
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   └── training_splits/
    │
    ├── data.dvc
    ├── dvc.yaml
    ├── .dvc/
    ├── Dockerfile
    ├── docker-shell.sh
    ├── docker-entrypoint.sh
    ├── pyproject.toml
    ├── uv.lock
    └── README.md  ← this file

"""