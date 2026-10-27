# ==============================================================================
# NexusCTI Production Dockerfile
# Multi-modal Cyber Threat Attribution Engine (GNN + Dense-Sparse Hybrid RAG)
# ==============================================================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    NEXUSCTI_HOST=0.0.0.0 \
    NEXUSCTI_PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY nexuscti/ ./nexuscti/
COPY web/ ./web/
COPY start_server.py .
COPY run_benchmark.py .
COPY run_demo.py .
COPY generate_pdf_report.py .

# Create artifacts directory
RUN mkdir -p /app/artifacts

# Expose FastAPI service port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default launch command
CMD ["python", "start_server.py"]
