# Use Python 3.11 slim image for FastAPI backend
FROM python:3.11-slim as fastapi-builder

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Backend Python dependencies (repo ships backend/requirements.txt)
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Multi-stage build for Streamlit dashboard
FROM python:3.11-slim as streamlit-builder

WORKDIR /app/dashboard

# Install system dependencies for Streamlit
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY dashboard/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Final runtime image combining both
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directories
RUN mkdir -p /app/backend /app/dashboard
WORKDIR /app

# Copy backend from builder
COPY --from=fastapi-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=fastapi-builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY backend/ /app/backend/
COPY dashboard/ /app/dashboard/

# Optional env file (provide .env in build context or use runtime env vars)
COPY .env.example /app/.env

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start both services using a startup script
COPY start.sh /app/
RUN chmod +x /app/start.sh

CMD ["bash", "/app/start.sh"]
