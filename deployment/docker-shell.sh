#!/bin/bash

# exit immediately if a command exits with a non-zero status
#set -e

# Define some environment variables
export IMAGE_NAME="dnd-master-deployment"
# Use absolute path to avoid issues with symlinks or Trash
# Use realpath if available, otherwise use pwd -P to resolve symlinks
if command -v realpath >/dev/null 2>&1; then
    export BASE_DIR=$(realpath "$(dirname "$0")")
else
    export BASE_DIR=$(cd "$(dirname "$0")" && pwd -P)
fi
# Check if we're in Trash (shouldn't happen, but just in case)
if [[ "$BASE_DIR" == *".Trash"* ]]; then
    echo "ERROR: Deployment folder appears to be in Trash: $BASE_DIR"
    echo "Please restore it from Trash or use the correct location."
    exit 1
fi
export SECRETS_DIR=$(cd "$BASE_DIR/../../secrets" && pwd -P)
export SSH_DIR="$SECRETS_DIR"
# export SECRETS_DIR=$(pwd)/../../secrets/ac215-project/
# export SSH_DIR=$(pwd)/../../secrets/ac215-project/
export GCP_PROJECT="even-turbine-471117-u0" # Change to your GCP Project
export GCP_REGION="us-central1"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/deployment.json
export PULUMI_BUCKET="gs://$GCP_PROJECT-pulumi-state-bucket"

# Create local Pulumi plugins directory if it doesn't exist
mkdir -p "$BASE_DIR/pulumi-plugins"

# Debug: Show paths being used
echo "BASE_DIR: $BASE_DIR"
echo "SECRETS_DIR: $SECRETS_DIR"
echo "PROJECT_ROOT will be: $(cd "$BASE_DIR/.." && pwd -P)"

# Check if container is already running
if docker ps --format "table {{.Names}}" | grep -q "^${IMAGE_NAME}$"; then
    echo "Container '${IMAGE_NAME}' is already running. Shelling into existing container..."
    # Use --workdir to explicitly set working directory, avoiding mount namespace issues
    docker exec -it --workdir /app $IMAGE_NAME /bin/bash
else
    echo "Container '${IMAGE_NAME}' is not running. Building and starting new container..."

    # Build the image based on the Dockerfile
    #docker build -t $IMAGE_NAME -f Dockerfile .
    docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

    # Run the container
    # Mount project root so we can access src/ directory
    # From deployment, go up 1 level to reach project root
    PROJECT_ROOT=$(cd "$BASE_DIR/.." && pwd -P)
    
    # Verify paths don't contain Trash
    if [[ "$BASE_DIR" == *".Trash"* ]] || [[ "$PROJECT_ROOT" == *".Trash"* ]]; then
        echo "ERROR: Paths contain .Trash - this will cause Docker mount issues"
        echo "BASE_DIR: $BASE_DIR"
        echo "PROJECT_ROOT: $PROJECT_ROOT"
        echo "Please ensure the deployment folder is not in Trash"
        exit 1
    fi
    docker run --rm --name $IMAGE_NAME -ti \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$BASE_DIR":/app \
    -v "$PROJECT_ROOT":/project-root \
    -v "$SECRETS_DIR":/secrets \
    -v "$SSH_DIR/.ssh":/home/app/.ssh:ro \
    -v "$BASE_DIR/docker_config.json":/root/.docker/config.json \
    -v "$BASE_DIR/pulumi-plugins":/root/.pulumi/plugins \
    -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
    -e USE_GKE_GCLOUD_AUTH_PLUGIN=True \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e GCP_REGION=$GCP_REGION \
    -e GCP_ZONE=$GCP_ZONE \
    -e PULUMI_BUCKET=$PULUMI_BUCKET \
    $IMAGE_NAME
fi
