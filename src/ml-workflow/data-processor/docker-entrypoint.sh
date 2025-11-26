#!/bin/bash
set -e

echo "============================================"
echo "🚀 DnD Data Processor Container Started"
echo "============================================"
echo "Architecture: $(uname -m)"
echo "Python version: $(python --version)"

if command -v uv &> /dev/null; then
    echo "UV version: $(uv --version)"
else
    echo "UV version: Not found (using pip environment)"
fi

echo "GCP_PROJECT=${GCP_PROJECT}"
echo "GCS_BUCKET_NAME=${GCS_BUCKET_NAME}"
echo "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}"
echo "--------------------------------------------"

echo "🔧 Activating virtual environment (if exists)..."
if [ -f "/.venv/bin/activate" ]; then
    source /.venv/bin/activate || true
fi

# ============================================================
# Logic Branching 
# ============================================================

# Case 1 — No arguments → default to processor.py
if [[ $# -eq 0 ]]; then
    echo "💡 No arguments provided → running default: processor.py"
    
    # Use exec so python becomes PID 1 (correct container behavior)
    exec python processor.py
fi

# Case 2 — Custom command
echo "▶️ Executing custom command: $@"
exec "$@"
