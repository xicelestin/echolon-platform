# Echolon Platform - Troubleshooting FAQ

**Last Updated:** December 2024  
**For:** Cloud Run deployment, backend issues, and common problems

---

## Deployment Issues

### Q: GitHub Actions workflow fails to deploy
**Symptoms:** `Backend Deploy` workflow shows red X

**Solutions:**
1. Check GitHub Actions logs for specific error
2. Verify GCP service account has permissions
3. Check if Docker build succeeded
4. Try deploying with `main_minimal.py` first (see `backend/README_MINIMAL.md`)

**Quick Fix:**
```bash
# Deploy minimal version to test
# In backend/Dockerfile, change:
CMD ["uvicorn", "main_minimal:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Q: Docker build fails with dependency errors
**Symptoms:** Error installing Python packages

**Solutions:**
1. Check `requirements.txt` for typos
2. Verify all package versions are valid
3. Try building locally: `docker build -t test backend/`
4. Check if pip can resolve dependencies

### Q: Cloud Run service won't start
**Symptoms:** Service status stuck on "Deploying" or immediately fails

**Solutions:**
1. Check logs: `gcloud logging read`
2. Verify environment variables are set
3. Check database connection (if using full backend)
4. Verify port 8080 is exposed
5. Test minimal version first

---

## Backend/API Issues

### Q: Health check endpoint returns 404
**Symptoms:** `curl /health` returns "Not Found"

**Solutions:**
1. Verify service URL is correct
2. Check if Cloud Run service is "Ready"
3. Test with full URL: `https://SERVICE-URL/health`
4. Check if FastAPI app is running

**Test Command:**
```bash
curl -v https://YOUR-URL/health
```

### Q: Database connection fails
**Symptoms:** "Could not connect to PostgreSQL" errors

**Solutions:**
1. Verify `DATABASE_URL` environment variable
2. Check if Cloud SQL instance is running
3. Verify service account has Cloud SQL Client role
4. Test connection string format
5. Use minimal version to bypass database

**Connection String Format:**
```
postgresql://USER:PASSWORD@/DATABASE?host=/cloudsql/PROJECT:REGION:INSTANCE
```

### Q: ML endpoints timeout
**Symptoms:** 504 Gateway Timeout on `/ml/train` or `/ml/forecast`

**Solutions:**
1. Increase Cloud Run timeout (currently 600s)
2. Move long-running tasks to background jobs
3. Check dataset size (large datasets take longer)
4. Monitor Cloud Run memory usage

**Adjust Timeout:**
```bash
gcloud run services update echolon-backend \
  --timeout=900 \
  --region=us-central1
```

---

## Data/CSV Issues

### Q: CSV upload fails with "Invalid format" error
**Symptoms:** 400 error when uploading CSV

**Solutions:**
1. Verify CSV has headers in first row
2. Check for special characters in column names
3. Ensure comma-separated (not semicolon)
4. Verify date columns are in YYYY-MM-DD format
5. Check file size (max 100 MB)

**Valid CSV Example:**
```csv
date,sales,inventory
2024-01-01,1250.50,450
2024-01-02,1300.25,425
```

### Q: Model training fails
**Symptoms:** Training job status shows "failed"

**Solutions:**
1. Check if dataset has enough rows (minimum 30)
2. Verify date column is properly formatted
3. Check for missing or null values
4. Ensure numeric columns don't have text
5. Review training job logs

---

## Performance Issues

### Q: API responses are slow
**Symptoms:** Requests take > 5 seconds

**Solutions:**
1. Check Cloud Run metrics for CPU/memory usage
2. Increase Cloud Run resources
3. Add database indexing
4. Implement caching
5. Monitor cold start times

**Increase Resources:**
```bash
gcloud run services update echolon-backend \
  --memory=2Gi \
  --cpu=2 \
  --region=us-central1
```

### Q: Cold starts are slow
**Symptoms:** First request after idle takes 10+ seconds

**Solutions:**
1. Set minimum instances: `--min-instances=1`
2. Reduce Docker image size
3. Use minimal version for testing
4. Implement warm-up requests

---

## Authentication/Authorization Issues

### Q: API returns 401 Unauthorized
**Symptoms:** All requests return "Unauthorized"

**Solutions:**
1. Verify API key is included in header
2. Check header format: `Authorization: Bearer YOUR_KEY`
3. Verify API key hasn't expired
4. Check if authentication is enabled

### Q: CORS errors in browser
**Symptoms:** "CORS policy" error in browser console

**Solutions:**
1. Check if CORS is enabled in FastAPI
2. Add frontend URL to allowed origins
3. Verify preflight OPTIONS requests work

---

## Testing Issues

### Q: Smoke tests fail
**Symptoms:** `./smoke_tests.sh` shows failures

**Solutions:**
1. Verify BASE_URL is correct in script
2. Check if service is actually deployed
3. Run tests one by one to isolate issue
4. Check Cloud Run logs during test run

**Run Single Test:**
```bash
curl https://YOUR-URL/health
```

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'X'"
**Cause:** Missing Python dependency  
**Fix:** Add package to `requirements.txt`

### "Port 8080 is not exposed"
**Cause:** Docker EXPOSE directive missing  
**Fix:** Add `EXPOSE 8080` to Dockerfile

### "Service account does not have required permissions"
**Cause:** GCP IAM roles not configured  
**Fix:** Grant Cloud Run Admin and Artifact Registry Writer roles

### "Cloud SQL connection refused"
**Cause:** Cloud SQL proxy not configured  
**Fix:** Add Cloud SQL connection string to DATABASE_URL

---

## Getting More Help

### Check Documentation
- **Full Debugging:** `docs/BACKEND_DEBUG.md`
- **Quick Reference:** `docs/QUICK_DEBUG_RUNBOOK.md`
- **Deployment Guide:** `docs/DEPLOYMENT_CHECKLIST.md`
- **API Docs:** `docs/API_ENDPOINTS.md`

### Debug Commands

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Check service status
gcloud run services describe echolon-backend --region=us-central1

# List revisions
gcloud run revisions list --service=echolon-backend --region=us-central1

# Test health endpoint
curl -v https://YOUR-URL/health

# Check GitHub Actions status
gh run list --workflow="Backend Deploy"
```

### Still Stuck?

1. **Check logs first** - 90% of issues are visible in logs
2. **Try minimal version** - Isolate if issue is deployment or code
3. **Test locally** - Run Docker container locally
4. **Ask for help** - Open GitHub issue with:
   - Error message
   - Steps to reproduce
   - Logs
   - What you've already tried

---

**Pro Tip:** When debugging, always start with the simplest version (minimal backend) and add complexity one piece at a time.
