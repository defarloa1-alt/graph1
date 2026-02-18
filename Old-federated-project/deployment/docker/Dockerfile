# Enhanced Federated Graph Framework - Production Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY src/ ./src/
COPY *.py ./
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/reports /app/version_snapshots

# Create non-root user
RUN groupadd -r framework && useradd -r -g framework framework
RUN chown -R framework:framework /app
USER framework

# Expose ports
EXPOSE 8080 8081 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "main.py"]
