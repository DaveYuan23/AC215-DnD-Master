#!/bin/bash
set -e

echo "==============================================="
echo "🚀 Building & Launching DnD Workflow Container"
echo "==============================================="

# ----- Configuration -----
export IMAGE_NAME="dnd-workflow"
export BASE_DIR=$(pwd)

# 你之前漏掉这个！！！！
export PERSISTENT_DIR="$BASE_DIR/../../../persistent-folder"

export SECRETS_DIR="$HOME/Desktop/secrets"

export GCP_PROJECT="even-turbine-471117-u0"
export GCP_LOCATION="us-central1"     # 用 LOCATION 不用 REGION
export GCS_BUCKET_NAME="ac215-ml-workflow-central1"

export GCS_PACKAGE_URI="gs://ac215-ml-workflow-central1/model-training"
export GCS_SERVICE_ACCOUNT="ml-workflow@even-turbine-471117-u0.iam.gserviceaccount.com"

echo "🧩 Project: $GCP_PROJECT"
echo "📍 Location:  $GCP_LOCATION"
echo "🪣 Bucket:  $GCS_BUCKET_NAME"
echo "🔐 Service Account: $GCS_SERVICE_ACCOUNT"
echo "-----------------------------------------------"

# ----- Build Docker image -----
echo "🐳 Building Docker image..."
docker build --platform=linux/amd64 -t $IMAGE_NAME -f Dockerfile .

# ----- Run Docker container -----
echo "🚀 Starting container..."

docker run --rm -ti \
  -v "$BASE_DIR":/app \
  -v "$PERSISTENT_DIR":/persistent \
  -v "$SECRETS_DIR":/secrets \
  -e GCP_PROJECT="$GCP_PROJECT" \
  -e GCS_BUCKET_NAME="$GCS_BUCKET_NAME" \
  -e GCP_LOCATION="$GCP_LOCATION" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json \
  "$IMAGE_NAME" \
  "$@"
