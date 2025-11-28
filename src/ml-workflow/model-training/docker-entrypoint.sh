#!/bin/bash
set -e

echo "============================================"
echo "🚀 AC215 Model Training Container Started"
echo "============================================"
echo "Architecture: $(uname -m)"
echo "Python version: $(python --version)"

if command -v uv &> /dev/null; then
    echo "UV version: $(uv --version)"
fi
echo "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}"
echo "--------------------------------------------"

# ------------------------------------------------------------
# Activate virtual environment
# ------------------------------------------------------------
if [ -f "/.venv/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source /.venv/bin/activate
fi
export PYTHONPATH="/app:$PYTHONPATH"
# ------------------------------------------------------------
# Sanity check: configs folder must be mounted
# ------------------------------------------------------------
if [ ! -d "/app/configs" ]; then
    echo "❌ ERROR: /app/configs not found."
    echo "You must mount configs:"
    echo "    -v <host>/configs:/app/configs"
    exit 1
fi

if [ ! -f "/app/configs/training_config.yaml" ]; then
    echo "❌ ERROR: training_config.yaml missing in /app/configs."
    exit 1
fi

# ------------------------------------------------------------
# If no args → drop into shell (safe default)
# ------------------------------------------------------------
if [[ $# -eq 0 ]]; then
    echo "💡 No command provided."
    echo "👉 Entering interactive shell."
    echo "You may run:"
    echo "    python trainer/task.py tune --epochs 3"
    echo "--------------------------------------------"
    exec /bin/bash
fi

# ------------------------------------------------------------
# Run the provided arguments
# ------------------------------------------------------------
echo "▶️ Executing command: $@"
exec "$@"
