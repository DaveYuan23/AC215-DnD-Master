#!/bin/bash

echo "Container is running!!!"
echo "Architecture: $(uname -m)"
echo "Python version: $(python --version)"
echo "UV version: $(uv --version)"

# Authenticate service account
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# Mount GCS bucket
mkdir -p /mnt/gcs_data
gcsfuse --key-file=$GOOGLE_APPLICATION_CREDENTIALS $GCS_BUCKET_NAME /mnt/gcs_data
echo 'GCS bucket mounted at /mnt/gcs_data'

# Activate virtual environment
echo "Activating virtual environment..."
source /.venv/bin/activate

# Keep a shell open
exec /bin/bash
