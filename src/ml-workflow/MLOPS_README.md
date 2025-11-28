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

# Project Structure

```
src/ml-workflow/
├── configs/                 # Centralized YAML configurations
│   ├── processor_config.yaml
│   └── training_config.yaml
├── data-collector/          # Container for raw data ingestion
├── data-processor/          # Container for cleaning & splitting (JSONL generation)
├── model-training/          # Container for Vertex AI SDK interaction
├── workflow/                # Orchestrator (CLI & Docker-in-Docker logic)
├── persistent/              # Local mount for logs and temp files
```

# Pipeline Architecture

```
      Data Collector
             ↓
      Data Processor
  (clean → jsonl → upload)
             ↓
  Gemini Fine-Tune Trigger
             ↓
   Lunch Auto Training Pipeline
```

---

# Data Acquisition (data-collector/)

The data-collector module retrieves raw CRD3 snapshots and stores them in versioned folders:
`gs://ac215-ml-workflow/dnd-ml-dataset-raw`

# Data Processing (data-processor/)
The data processor is fully containerized for reproducibility. It cleans, normalizes, and converts raw CRD3 messages into Gemini SFT fine-tuning JSONL format.

The processor performs:

- Field normalization (context/response extraction)
- Subsetting (controlled by env SUBSET_SIZE)
- Train/val/test splitting (configurable)
- Uploading versioned outputs to GCS via bucket: `gs://ac215-ml-workflow/dnd-ml-dataset-processor`

Save example like: `gs://ac215-ml-workflow/dnd-ml-dataset-processor/processor_v1.0.0/`

The processor also stores a config snapshot, ensuring dataset + config match the training job exactly.

# Model Training & Fine-Tuning (model-training/)

Fine-tuning is executed using Gemini 2.5 Flash through the AC215 Instructor Project:

```
project_id: 542859696336
location:   us-central1
base_model: gemini-2.5-flash
```

The trainer container loads:
- training_config.yaml
- versioned dataset URIs
- hyperparameters such as epochs, learning rate, and dataset shard sizes
- Fine-tuning is triggered via the Google GenAI SDK
- All jobs are logged under persistent/training_runs/.

# Workflow (Running the Pipeline)
You can run the entire workflow with a single command using the orchestrator script:

```
# Run full pipeline (Processor -> Trainer) with 3 epochs
cd workflow
./docker-shell.sh run-all --epochs 3
```

# Key Results
End-to-end pipeline executed successfully, including:
- Containerized processor run
- Automatic dataset versioning
- Vertex AI tuning job creation
- A Gemini SFT job was successfully submitted to Vertex AI and accepted by the backend.
- The fine-tuned model artifact is tracked by Vertex and is accessible via the TuningJob ID for further deployment.

# Model Design Choices
1. Base Model
We use Gemini 2.5 Flash because: Fine-tuned Gemini-Flash is significantly faster and more consistent for story-continuation tasks than base models.

2. Version-controlled Model Artifacts
Each TuningJob produces a model snapshot uniquely linked to:
- processor version
- config version
- dataset version
This allows fully traceable rollbacks and A/B comparisons.

3. Config-Driven Development
All hyperparameters (epochs, batch size) and data paths are decoupled from code, managed via YAML files in configs/.

4. Containerization
Every step (Collector, Processor, Trainer) runs in isolated Docker containers to ensure environment consistency.

5. Data Versioning
Processed datasets are stored in versioned GCS paths (e.g., processor_v1.0.0/) to prevent data drift issues.

6. Experiment Trackin
Every training run generates a unique timestamped log folder in persistent/training_runs/ containing a snapshot of the configuration and the job request payload.