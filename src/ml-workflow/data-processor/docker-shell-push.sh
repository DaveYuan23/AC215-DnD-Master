#!/bin/bash
set -e

###############################################
# DnD Data Processor - Build & Push Script
###############################################

export IMAGE_NAME="dnd-processor"
export PROJECT_ID="ac215"
export REGION="us-central1"
export REPO_NAME="ml-workflow"

export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"

echo "============================================"
echo "📦 Building & Pushing Data Processor Image"
echo "--------------------------------------------"
echo "Image URI:"
echo "  → $IMAGE_URI"
echo "============================================"


# =====================================================
# Step 1 — Set up buildx (multi-arch builder)
# =====================================================

if docker buildx inspect multi-arch >/dev/null 2>&1; then
    echo "🧹 Removing existing multi-arch builder..."
    docker buildx rm multi-arch
fi

echo "🔧 Creating new multi-arch builder..."
docker buildx create --driver-opt network=host --use --name multi-arch


# =====================================================
# Step 2 — Build & Push Image
# =====================================================

echo "🚀 Building & pushing image to Artifact Registry..."

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t "$IMAGE_URI" \
  -f Dockerfile .

echo "============================================"
echo "✅ Processor Image Build & Push Complete"
echo "   → $IMAGE_URI"
echo "============================================"
