# GitHub to GCP Cloud Run CI/CD Setup Guide

This document provides step-by-step instructions for configuring continuous integration and deployment (CI/CD) from GitHub to Google Cloud Platform's Cloud Run service.

## Architecture Overview

**Deployment Flow:**
1. Push code to main branch
2. GitHub Actions workflows trigger automatically
3. Docker images are built and pushed to Artifact Registry
4. Cloud Run services are deployed with new images
5. Services become available at their respective URLs

**Services:**
- **Backend (FastAPI)**: `echolon-api` → echolon-api Cloud Run service
- **Frontend (Streamlit)**: `echolon-dashboard` → echolon-dashboard Cloud Run service

**Infrastructure:**
- Project ID: `echelon-475606`
- Region: `us-west1` (Oregon)
- Container Registry: Artifact Registry
- Authentication: Workload Identity Federation (WIF)

## GitHub Secrets Configuration

These secrets must be configured in your GitHub repository settings before deployments can proceed.

### Required Secrets

#### 1. **WIF_PROVIDER** (Workload Identity Federation Provider)
The resource name of your Workload Identity Federation provider.

**Format:**
```
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID
```

**Example Value:**
```
projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

**How to obtain:**
```bash
gcloud iam workload-identity-pools providers describe PROVIDER_ID \
  --workload-identity-pool=github-pool \
  --location=global \
  --format='value(name)'
```

#### 2. **WIF_SERVICE_ACCOUNT** (Service Account Email)
The email address of the service account that GitHub Actions will assume.

**Format:**
```
SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com
```

**Current Value:**
```
echolon-backend-sa@echelon-475606.iam.gserviceaccount.com
```

**How to obtain:**
```bash
gcloud iam service-accounts list --project=echelon-475606 \
  --format='value(email)'
```

#### 3. **DATABASE_URL** (Optional for Backend)
Connection string for Cloud SQL PostgreSQL database.

**Format:**
```
postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

**Example:**
```
postgresql+asyncpg://postgres:PASSWORD@34.83.31.142:5432/echelon_db
```

**Notes:**
- PASSWORD should be stored securely in GCP Secret Manager (not in GitHub)
- Host: `34.83.31.142` (Cloud SQL public IP)
- Port: `5432` (PostgreSQL default)
- Database: `echelon_db`

### Configuring Secrets in GitHub

1. Navigate to your repository: `https://github.com/echolon44/echolon-platform`
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret from the list above
5. Verify all secrets are present before triggering deployments

**Secrets Checklist:**
- [ ] `WIF_PROVIDER` - Workload Identity Federation provider resource name
- [ ] `WIF_SERVICE_ACCOUNT` - Service account email
- [ ] `DATABASE_URL` - Cloud SQL connection string

## First-Time Deployment Instructions

### Prerequisites

1. **GitHub Secrets Configured** ✓ (All three secrets added to repository)
2. **GCP Project Setup** ✓ (Cloud SQL, Artifact Registry, Cloud Run services created)
3. **Dockerfiles Present** ✓ (backend/Dockerfile and dashboard/Dockerfile in repository)
4. **Code Ready** ✓ (All application code committed to main branch)

### Deployment Steps

#### Step 1: Trigger Workflow (Backend)

```bash
# Make a change to backend code and push
git add backend/
git commit -m "feat: initial backend deployment"
git push origin main
```

This automatically triggers `.github/workflows/backend-deploy.yml`

#### Step 2: Monitor Deployment

1. Go to **Actions** tab in GitHub repository
2. Click on the running workflow
3. View logs in real-time:
   - **Checkout code** - Repository cloned
   - **Authenticate to Google Cloud** - WIF authentication
   - **Build Docker image** - Image built locally
   - **Push Docker image** - Image pushed to Artifact Registry
   - **Deploy to Cloud Run** - Service deployed

#### Step 3: Verify Deployment

```bash
# Check service status
gcloud run services describe echolon-api \
  --region=us-west1 \
  --project=echelon-475606

# Get service URL
gcloud run services describe echolon-api \
  --region=us-west1 \
  --project=echelon-475606 \
  --format='value(status.url)'
```

**Test the API:**
```bash
curl https://echolon-api-us-west1-echelon-475606.run.app/health
```

#### Step 4: Deploy Frontend (Streamlit Dashboard)

```bash
# Make a change to dashboard code and push
git add dashboard/
git commit -m "feat: initial dashboard deployment"
git push origin main
```

This automatically triggers `.github/workflows/frontend-deploy.yml`

#### Step 5: Verify Frontend

```bash
# Get dashboard URL
gcloud run services describe echolon-dashboard \
  --region=us-west1 \
  --project=echelon-475606 \
  --format='value(status.url)'
```

**Access the dashboard in browser:**
```
https://echolon-dashboard-us-west1-echelon-475606.run.app
```

## Service Configuration Details

### Backend Service (echolon-api)

| Setting | Value |
|---------|-------|
| Memory | 1 Gi |
| CPU | 1 |
| Timeout | 3600 seconds |
| Max Instances | 100 |
| Port | 8000 |
| Authentication | Public (Allow Unauthenticated) |
| Cloud SQL Connection | echelon-475606:us-west1:echelon-db-dev |

### Frontend Service (echolon-dashboard)

| Setting | Value |
|---------|-------|
| Memory | 2 Gi |
| CPU | 2 |
| Timeout | 3600 seconds |
| Max Instances | 50 |
| Port | 8501 (Streamlit) |
| Authentication | Public (Allow Unauthenticated) |

## Environment Variables

### Backend Environment Variables

Set via `--update-env-vars` in Cloud Run deployment:

```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
LOG_LEVEL=info
```

### Frontend Environment Variables

Includes any Streamlit-specific configuration.

## Troubleshooting

### Common Issues

#### 1. WIF Authentication Fails

**Error:**
```
Error: Failed to authenticate to Google Cloud
```

**Solution:**
1. Verify `WIF_PROVIDER` secret is correct
2. Verify `WIF_SERVICE_ACCOUNT` secret is correct
3. Check service account has necessary IAM roles:
   - `roles/run.developer` - Deploy to Cloud Run
   - `roles/artifactregistry.writer` - Push to Artifact Registry
   - `roles/cloudsql.client` - Cloud SQL access

```bash
# Verify IAM bindings
gcloud projects get-iam-policy echelon-475606 \
  --flatten="bindings[].members" \
  --format='table(bindings.role)' \
  --filter="bindings.members:echolon-backend-sa@echelon-475606.iam.gserviceaccount.com"
```

#### 2. Docker Push Fails

**Error:**
```
Failed to push image to Artifact Registry
```

**Solution:**
1. Verify Artifact Registry repository exists: `echelon-docker`
2. Verify service account has `artifactregistry.writer` role
3. Check region matches: `us-west1`

#### 3. Cloud Run Deployment Fails

**Error:**
```
ERROR: (gcloud.run.deploy) Image pulls failed
```

**Solution:**
1. Verify image URI is correct
2. Check image exists in Artifact Registry
3. Verify service account has `artifactregistry.reader` role
4. Check Cloud Run service has permission to pull images

#### 4. Application Fails to Start

**Error:**
```
Container failed to start
```

**Solution:**
1. Check logs:
```bash
gcloud run logs read echolon-api --region=us-west1 --limit=50
```
2. Verify environment variables are set correctly
3. Verify database connection string is valid
4. Check Cloud SQL instance is running and accessible

## Rollback Procedures

### Rollback to Previous Deployment

```bash
# List recent revisions
gcloud run revisions list --service=echolon-api \
  --region=us-west1 \
  --project=echelon-475606

# Route traffic to previous revision
gcloud run services update-traffic echolon-api \
  --to-revisions=PREVIOUS_REVISION_ID=100 \
  --region=us-west1 \
  --project=echelon-475606
```

## Monitoring and Logs

### View Real-Time Logs

```bash
# Stream logs
gcloud run logs read echolon-api --region=us-west1 --follow

# View last 100 logs
gcloud run logs read echolon-api --region=us-west1 --limit=100
```

### Check Service Metrics

```bash
# Get service information
gcloud run services describe echolon-api --region=us-west1

# View recent revisions
gcloud run revisions list --service=echolon-api --region=us-west1
```

## Additional Resources

- [GitHub Actions for Google Cloud](https://github.com/google-github-actions)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Cloud SQL](https://cloud.google.com/sql/docs)
