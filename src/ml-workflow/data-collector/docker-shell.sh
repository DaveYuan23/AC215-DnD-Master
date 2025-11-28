#!/bin/bash
set -e

echo "========================================"
echo " Building & Running DND Data Collector"
echo "========================================"

# ---------- ENV CONFIG ----------
export IMAGE_NAME="dnd-data-collector"

# 当前 data-collector 文件夹
export BASE_DIR=$(pwd)

# secrets/ 与 persistent-folder/ 都在 repo 根目录
export PROJECT_ROOT=$(cd ../../.. && pwd)
export SECRETS_DIR="$PROJECT_ROOT/secrets"
export PERSISTENT_DIR="$PROJECT_ROOT/persistent-folder"

export GCP_PROJECT="even-turbine-471117-u0"
export GCS_BUCKET_NAME="ac215-ml-workflow"

echo "BASE_DIR       = $BASE_DIR"
echo "SECRETS_DIR    = $SECRETS_DIR"
echo "PERSISTENT_DIR = $PERSISTENT_DIR"
echo "GCP_PROJECT    = $GCP_PROJECT"
echo "GCS_BUCKET     = $GCS_BUCKET_NAME"
echo "========================================"


# ---------- BUILD IMAGE ----------
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .


# ---------- RUN CONTAINER ----------
docker run --rm -ti \
    -v "$BASE_DIR":/app \
    -v "$SECRETS_DIR":/secrets \
    -v "$PERSISTENT_DIR":/persistent \
    -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
    $IMAGE_NAME
