# ============================================================
# Model Training Container for AC215 DnD Project
# ============================================================

FROM python:3.12-slim-bookworm

# ------------------------------------------------------------
# Basic environment setup
# ------------------------------------------------------------
ARG DEBIAN_PACKAGES="build-essential git curl wget unzip gzip"

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV PATH="/.venv/bin:$PATH"

# uv environment
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/.venv

# ------------------------------------------------------------
# Install system dependencies + uv + create user + dirs
# ------------------------------------------------------------
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    pip install --no-cache-dir --upgrade pip && \
    pip install uv && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash app -d /home/app -u 1000 && \
    mkdir -p /app && chown app:app /app && \
    mkdir -p /persistent && chown app:app /persistent && \
    mkdir -p /.venv && chown app:app /.venv

# ------------------------------------------------------------
# Switch user
# ------------------------------------------------------------
USER app
WORKDIR /app

# ------------------------------------------------------------
# Install Python dependencies
# ------------------------------------------------------------
COPY --chown=app:app pyproject.toml uv.lock* ./
RUN uv sync --frozen

# ------------------------------------------------------------
# Copy trainer package code
# ------------------------------------------------------------
COPY --chown=app:app . ./

# ------------------------------------------------------------
# IMPORTANT: Config files are NOT baked into the image
# Config folder will be mounted at runtime:
#   -v "$BASE_DIR/../configs":/app/configs
# This respects the MLOps rule: "Immutable code, mutable config"
# ------------------------------------------------------------

# ------------------------------------------------------------
# Use docker-entrypoint.sh to handle CLI logic
# ------------------------------------------------------------
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
