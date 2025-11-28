#!/bin/bash
set -e

# ============================================================
# DnD Data Processor - Local Docker Shell
# ============================================================

export IMAGE_NAME="dnd-processor"

export BASE_DIR=$(pwd)

export CONFIGS_DIR="$BASE_DIR/../configs"

export SECRETS_DIR=$(pwd)/../../../secrets/

export PERSISTENT_DIR=$(pwd)/../../../persistent-folder/

export GCP_PROJECT="ac215"
export GCS_BUCKET_NAME="ac215-ml-workflow"

echo "============================================"
echo "Building Docker image for Data Processor..."
echo "Image Name: $IMAGE_NAME"
echo "Project: $GCP_PROJECT"
echo "Bucket: $GCS_BUCKET_NAME"
echo "============================================"

docker build --platform=linux/amd64 -t $IMAGE_NAME -f Dockerfile .

# ============================================================
# Launch container (interactive)
# ============================================================
echo "============================================"
echo "Starting DnD Data Processor container (interactive)..."
echo "Mounted paths:"
echo "  /app            -> $BASE_DIR"
echo "  /app/configs    -> $CONFIGS_DIR"
echo "  /app/secrets    -> $SECRETS_DIR"
echo "  /persistent     -> $PERSISTENT_DIR"
echo "============================================"

docker run --rm -it \
  -v "$BASE_DIR":/app \
  -v "$CONFIGS_DIR":/app/configs \
  -v "$SECRETS_DIR":/app/secrets \
  -v "$PERSISTENT_DIR":/persistent \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/llm-service-account.json \
  -e GCP_PROJECT=$GCP_PROJECT \
  -e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
  $IMAGE_NAME \
  /bin/bash

