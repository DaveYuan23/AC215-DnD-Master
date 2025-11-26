#!/bin/bash

set -e

############################################
# Paths
############################################

# Git repo root
export REPO_DIR="/Users/yz/Desktop/AC215_The_Bear_Dungeon"

# DV folder inside repo
export BASE_DIR="$REPO_DIR/src/data-versioning"

# Secrets folder
export SECRETS_DIR="$REPO_DIR/secrets"

############################################
# GCP config
############################################
export GCP_PROJECT="even-turbine-471117-u0"
export GCS_BUCKET_NAME="dnd-data-versioning"
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/llm-service-account.json"

############################################
# Image
############################################
export IMAGE_NAME="data-version-cli"

echo "-----------------------------------------"
echo " REPO_DIR:   $REPO_DIR"
echo " BASE_DIR:   $BASE_DIR"
echo " SECRETS:    $SECRETS_DIR"
echo "-----------------------------------------"

############################################
# Build (using DV folder as build context)
############################################
docker build -t $IMAGE_NAME -f $BASE_DIR/Dockerfile $BASE_DIR

############################################
# Run container
############################################
docker run --rm --name $IMAGE_NAME -ti \
    --privileged \
    --cap-add SYS_ADMIN \
    --device /dev/fuse \
    -v "$REPO_DIR":/repo \
    -v "$SECRETS_DIR":/secrets \
    -v ~/.gitconfig:/etc/gitconfig \
    -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
    -w /repo/src/data-versioning \
    $IMAGE_NAME
