# Backend Debugging Guide

## Overview

This guide provides comprehensive troubleshooting steps for debugging the Echolon AI FastAPI backend deployment on Google Cloud Run.

## Current Deployment Issue

**Symptom:** Container fails to start and listen on PORT=8080 within the allocated timeout

**Error Message:**
```
ERROR: (gcloud.run.deploy) The user-provided container failed to start and listen on the port defined by the PORT=8080 environment variable within the allocated timeout.
```

## Debugging Tools & Resources

### 1. Minimal Test Version (main_minimal.py)

A stripped-down version of the API with:
- No database dependencies
- Minimal imports (os, logging, fastapi)
- Basic endpoints (/, /health, /test)
- Comprehensive logging

**Usage:**
```bash
# Test locally
uvicorn main_minimal:app --host 0.0.0.0 --port 8080

# To use in deployment, modify Dockerfile CMD to:
CMD ["uvicorn", "main_minimal:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2. Startup Script (start.sh)

Comprehensive logging script that displays:
- Environment variables
- System information
- Python version and packages
- File system status
- Network configuration

**Usage:**
```bash
chmod +x start.sh
./start.sh
```

### 3. Cloud Run Logs

View deployment logs:
```bash
# Stream logs
gcloud run services logs tail echolon-api --project=echelon-475606

# View recent logs
gcloud run services logs read echolon-api --limit=100 --project=echelon-475606
```

## Common Issues & Solutions

### Issue 1: Import Errors

**Symptoms:**
- ModuleNotFoundError
- ImportError

**Solutions:**
1. Verify all dependencies in requirements.txt
2. Check Python version compatibility
3. Use minimal version first (main_minimal.py)

### Issue 2: Database Connection Failures

**Symptoms:**
- Connection timeout
- Authentication errors

**Solutions:**
1. Comment out database initialization in main.py:
   ```python
   # Base.metadata.create_all(bind=engine)
   ```
2. Verify DATABASE_URL secret is set
3. Check Cloud SQL proxy connection

### Issue 3: Port Binding Issues

**Symptoms:**
- Container starts but doesn't listen
- Health checks fail

**Solutions:**
1. Ensure uvicorn binds to 0.0.0.0:$PORT
2. Verify PORT environment variable
3. Check firewall rules

### Issue 4: Timeout During Startup

**Symptoms:**
- Container times out before ready

**Solutions:**
1. Increase timeout (already set to 600s)
2. Reduce startup operations
3. Use --no-traffic flag for gradual rollout

## Debugging Workflow

### Step 1: Test Minimal Version

1. Deploy with main_minimal.py
2. Verify basic connectivity
3. Check logs for startup sequence

### Step 2: Add Components Gradually

1. Add database connection (without table creation)
2. Add API endpoints one by one
3. Add ML/analytics features last

### Step 3: Monitor and Iterate

1. Check Cloud Run metrics
2. Monitor error logs
3. Test endpoints individually

## Environment Variables

### Required
- `PORT`: Container port (default: 8080)
- `LOG_LEVEL`: Logging level (default: info)

### Optional
- `DATABASE_URL`: PostgreSQL connection string
- `PYTHONUNBUFFERED`: Set to 1 for immediate log output

## Deployment Configuration

### Cloud Run Settings
```yaml
Memory: 1Gi
CPU: 1
Timeout: 600s (10 minutes)
Max Instances: 10
Platform: managed
```

### Health Checks
```
Endpoint: /health
Expected Response: {"status": "healthy"}
```

## Testing Checklist

- [ ] Dockerfile builds successfully
- [ ] Container runs locally
- [ ] Health endpoint responds
- [ ] All required env vars set
- [ ] Dependencies installed
- [ ] Logs show startup sequence
- [ ] Port binding confirmed
- [ ] Database connection (if enabled)

## Next Steps

If issues persist:
1. Review Cloud Run documentation
2. Check GCP service status
3. Verify IAM permissions
4. Contact GCP support

## Resources

- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Uvicorn Settings](https://www.uvicorn.org/settings/)

---

*Last Updated: 2025-11-30*
