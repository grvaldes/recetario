# Stage 1: Build & Runtime for Python FastAPI backend
FROM python:3.12-slim-bookworm

# Prevent Python from writing .pyc files and enable unbuffered streaming
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user with dedicated UID/GID
RUN groupadd -g 10001 appuser && \
  useradd -u 10001 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Install dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and migrations
COPY --chown=appuser:appuser . .

# Ensure upload directory exists and has correct permissions
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app/uploads

# Switch to non-root user
USER appuser

EXPOSE 8041

# Health check using python urllib
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8041/api/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8041"]
