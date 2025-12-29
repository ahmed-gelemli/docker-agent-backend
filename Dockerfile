# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r dockeragent && useradd -r -g dockeragent dockeragent

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/dockeragent/.local

# Copy application code
COPY --chown=dockeragent:dockeragent ./app /app/app
COPY --chown=dockeragent:dockeragent ./run.py /app/run.py

# Set PATH for user-installed packages
ENV PATH=/home/dockeragent/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER dockeragent

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9000/healthz')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:9000", "--access-logfile", "-", "--error-logfile", "-"]
