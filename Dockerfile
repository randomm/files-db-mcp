FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
# Note: First run will download large embedding models which can take several minutes
# The run.sh script handles this with a longer timeout, but Docker health checks need to be configured too
HEALTHCHECK --interval=30s --timeout=30s --start-period=600s --retries=10 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run when container starts
CMD ["python", "-m", "src.main"]