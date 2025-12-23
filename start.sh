#!/bin/bash
# Echolon Platform - Multi-Service Startup Script
# This script starts both FastAPI backend and Streamlit dashboard

set -e

echo "[$(date)] Starting Echolon Platform services..."

# Logging setup
LOG_DIR="/app/logs"
mkdir -p $LOG_DIR

# Export environment variables
export PYTHONUNBUFFERED=1
export LOG_DIR=$LOG_DIR

# Function to log messages
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_DIR/startup.log
}

# Function to wait for services
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=30
    local attempt=0

    log_message "Waiting for $service to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            log_message "$service is ready at $host:$port"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    log_message "Timeout waiting for $service"
    return 1
}

# Health check function
health_check() {
    local url=$1
    local service=$2
    local max_attempts=10
    local attempt=0

    log_message "Running health check for $service..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            log_message "Health check passed for $service"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log_message "Health check failed for $service"
    return 1
}

# Start FastAPI Backend Service
start_backend() {
    log_message "Starting FastAPI backend service..."
    
    cd /app/backend
    
    # Create necessary directories
    mkdir -p /app/logs
    
    # Start uvicorn server
    exec uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --log-level "${LOG_LEVEL:-info}" \
        --access-log \
        --use-colors \
        >> $LOG_DIR/backend.log 2>&1 &
    
    BACKEND_PID=$!
    log_message "FastAPI backend started with PID: $BACKEND_PID"
}

# Start Streamlit Dashboard Service
start_dashboard() {
    log_message "Starting Streamlit dashboard service..."
    
    cd /app/dashboard
    
    # Streamlit configuration
    export STREAMLIT_SERVER_PORT=8501
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_CLIENT_SHOWERRORDETAILS=false
    
    # Start streamlit app
    exec streamlit run app.py \
        --logger.level="${LOG_LEVEL:-info}" \
        >> $LOG_DIR/dashboard.log 2>&1 &
    
    DASHBOARD_PID=$!
    log_message "Streamlit dashboard started with PID: $DASHBOARD_PID"
}

# Graceful shutdown function
shutdown_handler() {
    log_message "Shutdown signal received. Terminating services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill -TERM $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill -TERM $DASHBOARD_PID 2>/dev/null || true
    fi
    
    wait $BACKEND_PID 2>/dev/null || true
    wait $DASHBOARD_PID 2>/dev/null || true
    
    log_message "Services terminated. Goodbye!"
    exit 0
}

# Set up signal handlers
trap shutdown_handler SIGTERM SIGINT

# Main startup sequence
log_message "Echolon Platform startup sequence initiated"
log_message "Environment: LOG_LEVEL=${LOG_LEVEL:-info}, NODE_ENV=${NODE_ENV:-production}"

# Start services
start_backend
start_dashboard

# Wait for services to be ready
sleep 5

# Health checks
if ! health_check "http://localhost:8000/health" "FastAPI Backend"; then
    log_message "WARNING: FastAPI backend health check failed"
fi

if ! health_check "http://localhost:8501" "Streamlit Dashboard"; then
    log_message "WARNING: Streamlit dashboard health check failed"
fi

log_message "Echolon Platform is now running"
log_message "FastAPI Backend: http://0.0.0.0:8000"
log_message "Streamlit Dashboard: http://0.0.0.0:8501"

# Keep services running
wait
