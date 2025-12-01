# ⚡ Cloud Run Quick Debug Runbook

**Last Updated:** 2025-11-30 | **For:** Echolon AI Backend

## 🚨 Emergency Commands

```bash
# View live logs
gcloud run services logs tail echolon-api --project=echelon-475606

# Check service status
gcloud run services describe echolon-api --region=us-west1 --project=echelon-475606

# Test health endpoint
curl https://echolon-api-[HASH].run.app/health
```

## 🔍 Common Issues & Quick Fixes

### Issue: Container fails to start
```bash
# 1. Check logs for error
gcloud run services logs read echolon-api --limit=50 | grep -i error

# 2. Verify environment variables
gcloud run services describe echolon-api --region=us-west1 \
  --format="value(spec.template.spec.containers[0].env)"

# 3. Test with minimal version
# Edit Dockerfile: CMD uvicorn main_minimal:app
```

### Issue: Import/Module errors
```bash
# Check requirements are installed
# Add to Dockerfile RUN section:
RUN pip list && echo "All packages installed"
```

### Issue: Database connection fails
```bash
# 1. Verify Cloud SQL connection
gcloud sql instances describe echelon-db-dev --project=echelon-475606

# 2. Comment out DB in main.py
# Base.metadata.create_all(bind=engine)
```

### Issue: Port binding
```bash
# Verify PORT env var in logs
echo $PORT  # Should be 8080

# Ensure uvicorn uses $PORT
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
```

## 📊 Debug Checklist (2 minutes)

- [ ] GitHub Actions workflow passed?
- [ ] Docker image pushed to Artifact Registry?
- [ ] Cloud Run service shows "Ready"?
- [ ] Health endpoint returns 200?
- [ ] Logs show "Uvicorn running"?
- [ ] No import errors in logs?
- [ ] DATABASE_URL set (if using DB)?
- [ ] Timeout set to 600s+?

## 🛠️ Debugging Tools

### Test Locally
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Visit http://localhost:8000
```

### Build Docker Locally
```bash
cd backend
docker build -t echolon-api-test .
docker run -p 8080:8080 -e PORT=8080 echolon-api-test
# Visit http://localhost:8080
```

### Check GitHub Actions
```bash
# View workflow runs
gh run list --workflow=backend-deploy.yml

# View specific run
gh run view [RUN_ID] --log
```

## 🎯 Quick Deployment Test

```bash
# 1. Make trivial change
echo "# $(date)" >> backend/main.py

# 2. Commit and push
git add backend/main.py
git commit -m "test: trigger deployment"
git push

# 3. Watch deployment (2-4 mins)
gh run watch

# 4. Test endpoint
curl https://echolon-api-[HASH].run.app/
```

## 📝 Log Analysis Patterns

```bash
# Find startup errors
gcloud run services logs read echolon-api --limit=100 | grep -E "(ERROR|CRITICAL|Failed|Exception)"

# Check PORT binding
gcloud run services logs read echolon-api --limit=100 | grep -i "port"

# View startup sequence
gcloud run services logs read echolon-api --limit=100 | grep -i "starting"

# Database connection attempts
gcloud run services logs read echolon-api --limit=100 | grep -i "database"
```

## 🔄 Rollback Procedure

```bash
# 1. List revisions
gcloud run revisions list --service=echolon-api --region=us-west1

# 2. Route traffic to previous revision
gcloud run services update-traffic echolon-api \
  --to-revisions=[PREVIOUS-REVISION]=100 \
  --region=us-west1

# 3. Verify
curl https://echolon-api-[HASH].run.app/health
```

## 🎨 Environment Variable Reference

| Variable | Required | Default | Purpose |
|----------|----------|---------|----------|
| PORT | Auto-set | 8080 | Container port |
| LOG_LEVEL | No | info | Logging verbosity |
| DATABASE_URL | Optional | - | PostgreSQL connection |
| PYTHONUNBUFFERED | Recommended | 1 | Real-time logs |

##  Performance Tuning

```yaml
# In backend-deploy.yml
--memory=1Gi        # Increase if OOM errors
--cpu=1             # Increase for better performance  
--timeout=600       # Increase if slow startup
--max-instances=10  # Increase for high traffic
--min-instances=1   # Set >0 to avoid cold starts
```

## 🆘 Escalation Path

1. Check BACKEND_DEBUG.md for detailed troubleshooting
2. Review recent commits: `git log --oneline -10`
3. Compare with last working version
4. Test with Dockerfile.debug for verbose output
5. Contact: GCP Support (if infrastructure issue)

## 📞 Quick Links

- [GCP Console - Cloud Run](https://console.cloud.google.com/run?project=echelon-475606)
- [GCP Console - Logs](https://console.cloud.google.com/logs?project=echelon-475606)
- [GitHub Actions](https://github.com/echolon44/echolon-platform/actions)
- [Artifact Registry](https://console.cloud.google.com/artifacts?project=echelon-475606)

---

**Pro Tip:** Keep this runbook open during deployments for instant access to debug commands!
