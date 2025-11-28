#!/bin/bash
set -e

echo "==============================================="
echo "🚀 Building & Launching DnD Workflow Container"
echo "==============================================="

# ----- Configuration -----
export IMAGE_NAME="dnd-workflow"
export BASE_DIR=$(pwd)                    # workflow 
export WORKFLOW_ROOT="$BASE_DIR/.."       # ml-workflow/
export CONFIGS_DIR="$WORKFLOW_ROOT/configs"
export PERSISTENT_DIR="$BASE_DIR/../../../persistent-folder"
export SECRETS_DIR="$BASE_DIR/../../../secrets"

export GCP_PROJECT="even-turbine-471117-u0"
export GCP_LOCATION="us-central1"
export GCS_BUCKET_NAME="ac215-ml-workflow"
export GOOGLE_APPLICATION_CREDENTIALS_PATH="/secrets/llm-service-account.json"

echo "🧩 Project: $GCP_PROJECT"
echo "📍 Location: $GCP_LOCATION"
echo "🪣 Bucket:   $GCS_BUCKET_NAME"
echo "📂 Configs:  $CONFIGS_DIR"
echo "-----------------------------------------------"

# ----- Build Docker image -----
echo "🐳 Building Docker image..."
docker build \
  --platform=linux/amd64 \
  -t $IMAGE_NAME \
  -f Dockerfile \
  .

# ----- Run Docker container -----
echo "🚀 Starting container..."

docker run --rm -it \
  -v "$BASE_DIR":/app \
  -v "$PERSISTENT_DIR":/persistent \
  -v "$SECRETS_DIR":/secrets \
  -v "$CONFIGS_DIR":/app/configs \
  \
  -e GCP_PROJECT="$GCP_PROJECT" \
  -e GCS_BUCKET_NAME="$GCS_BUCKET_NAME" \
  -e GCP_LOCATION="$GCP_LOCATION" \
  -e GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS_PATH" \
  \
  -e MOUNT_CONFIGS_DIR="$CONFIGS_DIR" \
  -e MOUNT_SECRETS_DIR="$SECRETS_DIR" \
  -e MOUNT_PERSIST_DIR="$PERSISTENT_DIR" \
  \
  -v /var/run/docker.sock:/var/run/docker.sock \
  "$IMAGE_NAME" \
  "$@"
