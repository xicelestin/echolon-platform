# Minimal Backend Deployment - Quick Start

**Purpose:** Lightweight FastAPI backend for testing Cloud Run deployments without database dependencies.

## What is `main_minimal.py`?

A stripped-down version of the Echolon backend that:
- ✅ Has NO database dependencies
- ✅ Tests Cloud Run deployment pipeline
- ✅ Verifies Docker container build
- ✅ Validates basic API routing
- ❌ Does NOT include ML training/forecasting
- ❌ Does NOT connect to PostgreSQL

## When to Use This

1. **Debugging deployment issues** - Test if Cloud Run works before adding complexity
2. **Testing GitHub Actions** - Verify CI/CD pipeline without full backend
3. **Learning Cloud Run** - Simple example for understanding deployments
4. **Quick health checks** - Fast startup for basic API verification

## Quick Deploy

### 1. Modify Dockerfile

In `backend/Dockerfile`, change line 27:

```dockerfile
# FROM:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# TO:
CMD ["uvicorn", "main_minimal:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2. Commit and Push

```bash
git add backend/Dockerfile
git commit -m "Deploy with minimal version for testing"
git push origin main
```

### 3. Monitor GitHub Actions

- Go to **Actions** tab in GitHub
- Watch `Backend Deploy` workflow
- Should complete in 3-5 minutes

### 4. Test the Deployment

```bash
# Get your Cloud Run URL
CLOUD_RUN_URL="https://YOUR-SERVICE-URL"

# Test health endpoint
curl $CLOUD_RUN_URL/health
# Expected: {"status": "healthy", "service": "echolon-minimal"}

# Test root endpoint
curl $CLOUD_RUN_URL/
# Expected: {"message": "Echolon Minimal API"}
```

## Available Endpoints

### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "service": "echolon-minimal",
  "timestamp": "2024-12-01T00:00:00Z"
}
```

### `GET /`
Root endpoint
```json
{
  "message": "Echolon Minimal API",
  "version": "minimal-1.0",
  "endpoints": ["/health", "/"]
}
```

## Reverting to Full Backend

Once testing is complete, revert `Dockerfile` to use `main:app`:

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Then commit and push:
```bash
git add backend/Dockerfile
git commit -m "Revert to full backend with database"
git push origin main
```

## Troubleshooting

### Deployment Fails
- Check `docs/QUICK_DEBUG_RUNBOOK.md`
- Review GitHub Actions logs
- Verify Dockerfile syntax

### Container Won't Start
- Check Cloud Run logs: `gcloud logging read`
- Verify port 8080 is exposed
- Check for Python import errors

### Health Check Fails
- Verify service URL is correct
- Check Cloud Run service is "Ready"
- Test with curl verbose: `curl -v $URL/health`

## File Structure

```
backend/
├── main.py              # Full backend (with database)
├── main_minimal.py      # Minimal backend (NO database)
├── Dockerfile           # Change CMD to switch versions
├── requirements.txt     # All dependencies
└── README_MINIMAL.md    # This file
```

## Related Documentation

- **Full Debugging:** `docs/BACKEND_DEBUG.md`
- **Quick Reference:** `docs/QUICK_DEBUG_RUNBOOK.md`
- **Deployment Checklist:** `docs/DEPLOYMENT_CHECKLIST.md`
- **API Documentation:** `docs/API_ENDPOINTS.md`

## Tips

1. **Always test minimal first** when debugging deployment issues
2. **Use this for CI/CD testing** without database setup
3. **Keep it simple** - Don't add features to minimal version
4. **Document changes** - Note when you switch between versions

---

**Questions?** Check `docs/TROUBLESHOOTING_FAQ.md` or open a GitHub issue.
