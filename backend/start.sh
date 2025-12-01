#!/bin/bash
# Comprehensive startup script with logging for Cloud Run debugging

set -e  # Exit on error

echo "======================================"
echo "Starting Echolon API Backend"
echo "======================================"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

# Display environment information
echo "[INFO] Environment Variables:"
echo "  PORT: ${PORT:-8080}"
echo "  LOG_LEVEL: ${LOG_LEVEL:-info}"
echo "  DATABASE_URL: ${DATABASE_URL:+***set***}"
echo "  PYTHONUNBUFFERED: ${PYTHONUNBUFFERED:-1}"
echo ""

# Display system information
echo "[INFO] System Information:"
echo "  Hostname: $(hostname)"
echo "  Working Directory: $(pwd)"
echo "  User: $(whoami)"
echo "  Python Version: $(python --version 2>&1)"
echo "  Pip Version: $(pip --version 2>&1)"
echo ""

# List Python packages
echo "[INFO] Installed Python Packages:"
pip list 2>&1 | head -20
echo "..."
echo ""

# Check for required files
echo "[INFO] Checking required files:"
for file in "main.py" "requirements.txt"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file NOT FOUND"
    fi
done
echo ""

# List directory contents
echo "[INFO] Current directory contents:"
ls -lah
echo ""

# Display network configuration
echo "[INFO] Network Configuration:"
echo "  Listening on: 0.0.0.0:${PORT:-8080}"
if command -v netstat &> /dev/null; then
    echo "  Active connections:"
    netstat -tuln 2>/dev/null | head -10 || echo "    (netstat not available)"
fi
echo ""

# Start the application
echo "======================================"
echo "Starting FastAPI with Uvicorn"
echo "======================================"

exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level ${LOG_LEVEL:-info}
