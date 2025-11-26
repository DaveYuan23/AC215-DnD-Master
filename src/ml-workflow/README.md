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
├── configs/
├── data-collector/
├── data-processor/
├── model-training/
├── workflow/
└── persistent/
└── README.Rmd
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


# Model Design Choices
1. Base Model

We use Gemini 2.5 Flash because:

High instruction-following accuracy

Fast fine-tuning iterations

Significantly lower cost

Proven stability for instruction→response tasks
