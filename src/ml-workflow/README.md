---
title: "DnD Narrator — Gemini Fine-Tuning MLOps Pipeline"
---

# Overview

This directory implements the complete ML workflow used to train and fine-tune a Gemini-based model for the D&D Knowledge Agent system. The workflow includes data acquisition, processing, model fine-tuning, and artifact versioning. All steps are fully containerized and reproducible.

- Data ingestion  
- Data preprocessing  
- JSONL dataset generation  
- Triggering Gemini fine-tuning jobs  
- Deploying tuned models to Vertex AI Endpoints  

The goal is to automatically retrain and redeploy the narrator model whenever new story data becomes available.

---

# Project Structure
'''
src/ml-workflow/
├── configs/                 # Centralized YAML configurations
│   ├── processor_config.yaml
│   └── training_config.yaml
├── data-collector/          # Container for raw data ingestion
├── data-processor/          # Container for cleaning & splitting (JSONL generation)
├── model-training/          # Container for Vertex AI SDK interaction
├── workflow/                # Orchestrator (CLI & Docker-in-Docker logic)
├── persistent/              # Local mount for logs and temp files
'''

# Pipeline Architecture

'''
      Data Collector
             ↓
      Data Processor
  (clean → jsonl → upload)
             ↓
  Gemini Fine-Tune Trigger
             ↓
   Deploy Tuned Model
'''

The pipeline is executed on Vertex AI using Kubeflow Pipelines.

---

# Data Acquisition (data-collector/)

The data-collector module retrieves raw CRD3 snapshots and stores them in versioned folders:
gs://ac215-ml-workflow/dnd-ml-dataset-raw

All computation and fine-tuning are performed on Google’s backend.

# Data Processing (data-processor/)
The data processor is fully containerized for reproducibility. It cleans, normalizes, and converts raw CRD3 messages into Gemini fine-tuning JSONL format.

Outputs are written to GCS via bucket:

gs://ac215-ml-workflow/dnd-ml-dataset-processor

# Model Training & Fine-Tuning (model-training/)

Fine-tuning is executed using Gemini 2.5 Flash through the AC215 Instructor Project:

'''
project_id = "542859696336"
location   = "us-central1"
'''

# Workflow (Running the Pipeline)
You can run the entire workflow with a single command using the orchestrator script:

'''
# Run full pipeline (Processor -> Trainer) with 3 epochs
cd workflow
./docker-shell.sh run-all --epochs 3
'''

# Model Design Choices
1. Base Model

We use Gemini 2.5 Flash because:

High instruction-following accuracy

Fast fine-tuning iterations

Significantly lower cost

Proven stability for instruction→response tasks

2. Key MLOps Features
Config-Driven Development: All hyperparameters (epochs, batch size) and data paths are decoupled from code, managed via YAML files in configs/.

Containerization: Every step (Collector, Processor, Trainer) runs in isolated Docker containers to ensure environment consistency.

Data Versioning: Processed datasets are stored in versioned GCS paths (e.g., processor_v1.0.0/) to prevent data drift issues.

Experiment Tracking: Every training run generates a unique timestamped log folder in persistent/training_runs/ containing a snapshot of the configuration and the job request payload.