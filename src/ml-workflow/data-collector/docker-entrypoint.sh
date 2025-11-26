#!/bin/bash
set -e

echo "=========================================="
echo " Starting DND Data Collector container"
echo "=========================================="
echo "Architecture: $(uname -m)"
echo "Python: $(python --version)"
echo "UV: $(uv --version)"
echo "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}"
echo "=========================================="

# Activate virtual environment
echo "Activating virtual environment..."
source /.venv/bin/activate

# If no arguments → run downloader by default
if [[ $# -eq 0 ]]; then
    echo "No arguments supplied → Running default: downloader.py"
    uv run python downloader.py
else
    echo "Arguments detected → Running downloader.py with args: $@"
    uv run python downloader.py "$@"
fi
