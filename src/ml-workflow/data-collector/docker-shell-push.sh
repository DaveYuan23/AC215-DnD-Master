#!/bin/bash
set -e

echo "========================================"
echo "   Building & Pushing Data Collector"
echo "========================================"

# ---------- CONFIG ----------
export PROJECT_ID="even-turbine-471117-u0"
export REGION="us-central1"
export REPO_NAME="ml-workflow"
export IMAGE_NAME="dnd-data-collector"

export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"

echo "Project ID:  $PROJECT_ID"
echo "Region:      $REGION"
echo "Repository:  $REPO_NAME"
echo "Image Name:  $IMAGE_NAME"
echo "Image URI:   $IMAGE_URI"
echo "========================================"


# ---------- Ensure auth for Artifact Registry ----------
echo "🔐 Configuring Docker for Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev


# ---------- Multi-arch builder ----------
if docker buildx inspect multi-arch >/dev/null 2>&1; then
    echo "🧹 Removing existing multi-arch builder..."
    docker buildx rm multi-arch
fi

echo "🔨 Creating new multi-arch builder..."
docker buildx create --driver-opt network=host --use --name multi-arch


# ---------- Build & Push ----------
echo "🚀 Building and pushing multi-architecture image..."
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t "$IMAGE_URI" \
  -f Dockerfile .

echo "✅ DONE! Image pushed to:"
echo "   $IMAGE_URI"
echo "========================================"
