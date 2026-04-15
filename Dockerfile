# Multi-stage Dockerfile for CyberShield
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app directory
WORKDIR /app

# Copy application code
COPY cybershield/ /app/cybershield/
COPY core/ /app/core/
COPY setup.py /app/
COPY README.md /app/
COPY MANIFEST.in /app/

# Install CyberShield
RUN pip install -e .

# Create data directories
RUN mkdir -p /root/.cybershield/logs \
    /root/.cybershield/models \
    /root/.cybershield/config \
    /root/.cybershield/data

# Expose P2P port
EXPOSE 8765

# Health check - use python to check if process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "cybershield" > /dev/null || exit 1

# Default command
CMD ["python", "-m", "cybershield.cli", "node", "monitor", "--p2p"]
