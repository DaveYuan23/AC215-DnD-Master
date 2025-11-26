#!/bin/bash
set -e

echo "============================================"
echo "🚀 DnD Data Processor Container Started"
echo "============================================"
echo "Architecture: $(uname -m)"
echo "Python version: $(python --version)"
echo "UV version: $(uv --version)"
echo "GCP_PROJECT=${GCP_PROJECT}"
echo "GCS_BUCKET_NAME=${GCS_BUCKET_NAME}"
echo "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}"
echo "--------------------------------------------"

echo "🔧 Activating virtual environment..."
source /.venv/bin/activate

# Default behavior → run processor.py
if [[ $# -eq 0 ]]; then
    echo "💡 No arguments provided → running default: processor.py"
    uv run python processor.py
    exit 0
fi

# Allow users to override command (advanced use)
echo "▶️ Running custom command: uv run python $@"
uv run python "$@"
