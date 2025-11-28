# ============================================================
# Workflow Orchestrator Container (Runs the MLOps CLI)
# ============================================================
FROM python:3.11-slim-bullseye

# ------------------------------------------------------------
# Environment variables
# ------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive
ENV UV_PROJECT_ENVIRONMENT=/.venv
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Ensure uv-installed binaries are available
ENV PATH="/.venv/bin:$PATH"

# ------------------------------------------------------------
# Install system dependencies
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    ca-certificates \
    gnupg \
    build-essential \
    docker.io \ 
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Install uv
# ------------------------------------------------------------
RUN pip install --no-cache-dir uv

# ------------------------------------------------------------
# Create runtime directory
# ------------------------------------------------------------
WORKDIR /app

# ------------------------------------------------------------
# Copy Python dep metadata
# ------------------------------------------------------------
COPY pyproject.toml uv.lock* ./

# ------------------------------------------------------------
# Install dependencies into /.venv
# ------------------------------------------------------------
RUN uv sync --frozen

# ------------------------------------------------------------
# Copy all project files
# ------------------------------------------------------------
COPY . .

# ------------------------------------------------------------
# Ensure entrypoint is executable
# ------------------------------------------------------------
RUN chmod +x docker-entrypoint.sh

# ------------------------------------------------------------
# Entrypoint (fixes Python path + command dispatch)
# ------------------------------------------------------------
ENTRYPOINT ["bash", "docker-entrypoint.sh"]

CMD ["python", "cli.py"]
