# Echolon Platform Deployment Checklist

**Purpose:** Step-by-step checklist for deploying backend changes to Cloud Run  
**Last Updated:** December 2024  
**Owner:** Echolon Team

---

## 🎯 Pre-Deployment Checklist

### Code Quality & Testing
- [ ] **Code review completed** - All changes reviewed and approved
- [ ] **Tests pass locally** - Run `pytest` or test suite
- [ ] **Smoke tests verified** - Run `./backend/smoke_tests.sh` against local instance
- [ ] **Database migrations tested** - Verify any schema changes work properly
- [ ] **Dependencies updated** - Check `requirements.txt` for any new packages
- [ ] **No hardcoded secrets** - All sensitive data uses environment variables

### Environment Configuration
- [ ] **Environment variables documented** - Check `backend/ENV_VARS.md` for required vars
- [ ] **Cloud Run secrets configured** - Verify secrets are set in GCP Secret Manager
- [ ] **Service account permissions** - Ensure service account has necessary IAM roles
- [ ] **Database credentials valid** - Test connection strings work
- [ ] **API keys active** - Verify third-party API keys are valid

### Documentation
- [ ] **CHANGELOG updated** - Document what's changing in this deployment
- [ ] **API docs updated** - If endpoints changed, update API documentation
- [ ] **README reflects changes** - Update README if setup process changed

---

## 🚀 Deployment Steps

### Step 1: Commit and Push
```bash
# Commit your changes
git add .
git commit -m "descriptive commit message"

# Push to main branch
git push origin main
```

### Step 2: Monitor GitHub Actions
1. **Navigate to Actions tab** in GitHub repository
2. **Watch deployment workflow** - `Backend Deploy` should trigger automatically
3. **Check build logs** - Look for any errors during:
   - Docker image build
   - Push to Google Artifact Registry
   - Cloud Run deployment

**Expected Duration:** 3-8 minutes

### Step 3: Verify Deployment Status
```bash
# Check Cloud Run service status
gcloud run services describe echolon-backend \
  --region=us-central1 \
  --platform=managed

# View recent revisions
gcloud run revisions list \
  --service=echolon-backend \
  --region=us-central1
```

### Step 4: Check Health Endpoints
```bash
# Test health endpoint
curl https://YOUR-SERVICE-URL/health

# Expected response: {"status": "healthy"}

# Test root endpoint
curl https://YOUR-SERVICE-URL/

# Expected response: {"message": "Echolon API", "version": "1.0"}
```

---

## ✅ Post-Deployment Validation

### Smoke Testing
- [ ] **Run smoke test suite** 
```bash
# Update BASE_URL in smoke_tests.sh to your Cloud Run URL
./backend/smoke_tests.sh
```

- [ ] **Test critical endpoints**
  - [ ] `GET /health` - Returns 200 OK
  - [ ] `GET /api/v1/` - Returns API info
  - [ ] `POST /api/v1/upload_csv` - Accepts file upload
  - [ ] `POST /ml/train` - Initiates training
  - [ ] `POST /ml/forecast` - Returns predictions
  - [ ] `GET /ml/insights` - Returns analysis

### Application Testing
- [ ] **Database connectivity** - Verify app can connect to PostgreSQL
- [ ] **File uploads work** - Test CSV upload functionality
- [ ] **ML endpoints respond** - Test forecasting and insights
- [ ] **Error handling works** - Test 404, 500 responses are properly formatted

### Monitoring & Logging
- [ ] **Check Cloud Run logs** 
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=echolon-backend" --limit=50
```

- [ ] **Monitor error rates** - Check Cloud Run metrics dashboard
- [ ] **Check startup logs** - Verify no errors during container initialization
- [ ] **Memory/CPU usage normal** - Monitor resource consumption

---

## 🔴 Rollback Procedure

If deployment fails or issues are detected:

### Quick Rollback
```bash
# List recent revisions
gcloud run revisions list --service=echolon-backend --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic echolon-backend \
  --region=us-central1 \
  --to-revisions=PREVIOUS-REVISION-NAME=100
```

### GitHub Actions Rollback
1. **Find last working commit** in GitHub history
2. **Revert to that commit**:
```bash
git revert HEAD
git push origin main
```
3. **Monitor new deployment** - GitHub Actions will deploy the revert

---

## 🐛 Troubleshooting Common Issues

### Deployment Fails
- **Check GitHub Actions logs** - Look for Docker build errors
- **Verify Dockerfile syntax** - Ensure no typos in `backend/Dockerfile`
- **Check dependencies** - Verify all packages in `requirements.txt` are valid

### Service Won't Start
- **Review Cloud Run logs** - Look for startup errors
- **Check environment variables** - Verify all required vars are set
- **Database connection** - Test database credentials
- **Refer to QUICK_DEBUG_RUNBOOK.md** - Emergency debugging guide

### Performance Issues
- **Increase memory/CPU** - Update Cloud Run service configuration
- **Check cold start times** - Consider minimum instances setting
- **Review database queries** - Optimize slow queries

### Timeout Errors
- **Increase request timeout** - Current setting: 600s (10 minutes)
- **Check long-running operations** - Move to async processing if needed
- **Review ML training time** - Consider background job processing

---

## 📋 Deployment Schedule

### Recommended Deployment Times
- **Best:** Monday-Thursday, 10 AM - 3 PM PT (low traffic window)
- **Avoid:** Friday afternoons, weekends (limited support availability)
- **Emergency deployments:** Document reason and notify team

### Communication
- [ ] **Notify team** - Announce deployment in team channel
- [ ] **Update status page** (if applicable)
- [ ] **Document deployment** - Log deployment time, version, changes

---

## 🔗 Related Resources

- **Debugging:** `docs/QUICK_DEBUG_RUNBOOK.md` - Emergency troubleshooting
- **Environment Variables:** `backend/ENV_VARS.md` - Complete env var reference
- **Testing:** `backend/smoke_tests.sh` - Automated endpoint testing
- **Architecture:** `docs/architecture.md` - System architecture overview
- **API Documentation:** `docs/API_ENDPOINTS.md` - Complete API reference

---

## ✨ Success Criteria

Deployment is successful when:
- ✅ GitHub Actions workflow completes without errors
- ✅ Cloud Run service status is "Ready"
- ✅ All smoke tests pass (10/10 tests passing)
- ✅ Health endpoint returns 200 OK
- ✅ No error spikes in Cloud Run logs
- ✅ Application responds to user requests
- ✅ Database connectivity confirmed

---

**Remember:** Always test locally before deploying to production. Use `main_minimal.py` to test basic deployment before full production deployment.

**Questions?** Refer to `docs/TROUBLESHOOTING_FAQ.md` or ping the team in #engineering.
