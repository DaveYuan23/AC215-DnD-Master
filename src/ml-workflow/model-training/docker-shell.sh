#!/bin/bash
set -e

# ======== Basic Environment Setup ========
export IMAGE_NAME="dnd-model-training"
export BASE_DIR=$(pwd)


export PERSISTENT_DIR=$(pwd)/../../../persistent-folder/
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCP_PROJECT_ID="ac215"
export GCS_BUCKET_NAME="ac215-ml-workflow"
export GCP_REGION="us-central1"
export GCS_PACKAGE_URI="gs://ac215-ml-workflow/model-training"

echo "============================================"
echo "Building Docker image for DnD Model Trainer..."
echo "============================================"
echo "Image:        $IMAGE_NAME"
echo "Project ID:   $GCP_PROJECT_ID"
echo "Region:       $GCP_REGION"
echo "Bucket:       $GCS_BUCKET_NAME"
echo "Package URI:  $GCS_PACKAGE_URI"
echo "Base Dir:     $BASE_DIR"
echo "Persistent:   $PERSISTENT_DIR"
echo "Secrets:      $SECRETS_DIR"
echo "============================================"

# ======== Build Image (amd64 for Vertex compatibility) ========
docker build \
  --platform=linux/amd64 \
  -t "$IMAGE_NAME" \
  -f Dockerfile .

echo "============================================"
echo "Starting training container (interactive)..."
echo "============================================"
echo "Mounted paths (inside container):"
echo "  /app            -> $BASE_DIR"
echo "  /app/configs    -> $BASE_DIR/../configs"
echo "  /app/secrets    -> $SECRETS_DIR"
echo "  /persistent     -> $PERSISTENT_DIR"
echo "============================================"

docker run --rm --name "$IMAGE_NAME" -ti \
    -v "$BASE_DIR":/app \
    -v "$BASE_DIR/../configs":/app/configs \
    -v "$SECRETS_DIR":/app/secrets \
    -v "$PERSISTENT_DIR":/persistent \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/llm-service-account.json \
    -e GCP_PROJECT="$GCP_PROJECT_ID" \
    -e GCS_BUCKET_NAME="$GCS_BUCKET_NAME" \
    -e GCP_REGION="$GCP_REGION" \
    -e GCS_PACKAGE_URI="$GCS_PACKAGE_URI" \
    "$IMAGE_NAME"

echo "============================================"
echo "Container execution finished."
echo "============================================"
