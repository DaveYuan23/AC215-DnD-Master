#!/bin/bash

set -e

export BASE_DIR=$(pwd)

# SECRETS LOCATION — YOU KEEP SECRETS ON DESKTOP
export SECRETS_DIR="$HOME/Desktop/secrets/"

# YOUR BUCKET
export GCS_BUCKET_NAME="dnd-data-versioning"

# YOUR PROJECT
export GCP_PROJECT="even-turbine-471117-u0"

# ZONE
export GCP_ZONE="us-central1-a"

# Inside-container path for service account key
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json"

echo "Building image"
docker build -t data-version-cli -f Dockerfile .

echo "Running container"
docker run --rm --name data-version-cli -ti \
--privileged \
--cap-add SYS_ADMIN \
--device /dev/fuse \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v ~/.gitconfig:/etc/gitconfig \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
data-version-cli
