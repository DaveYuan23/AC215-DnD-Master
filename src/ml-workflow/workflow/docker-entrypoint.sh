#!/bin/bash
set -e

echo "==============================================="
echo "🚀 Workflow container started"
echo "==============================================="

export PYTHONPATH="/app:$PYTHONPATH"

if [ -f "/.venv/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source /.venv/bin/activate
fi

if [ $# -eq 0 ]; then
    echo "💡 No command provided. Showing CLI help..."
    exec python cli.py --help
fi

case "$1" in
  collector|processor|trainer|run-all)
    echo "🔹 Running Workflow CLI: $@"
    exec python cli.py "$@"
    ;;

  *)
    echo "▶️ Executing system command: $@"
    exec "$@"
    ;;
esac
