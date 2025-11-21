# Echolon AI Platform - Deployment Guide

## Overview
This document outlines the deployment architecture and procedures for the Echolon AI platform on Google Cloud Platform (GCP).

## Architecture

### Components
1. **Backend API (FastAPI)**
   - Service: `echolon-backend`
   - Runtime: Python 3.11
   - Port: 8080
   - Memory: 1 Gi
   - CPU: 1

2. **Frontend Dashboard (Streamlit)**
   - Service: `echolon-dashboard`
   - Runtime: Python 3.11
   - Port: 8080
   - Memory: 1 Gi
   - CPU: 1

3. **Data Storage**
   - Cloud SQL (PostgreSQL)
   - Cloud Storage for file uploads

4. **Secrets Management**
   - Google Cloud Secret Manager
   - Environment variables for configuration

## Deployment Process

### Prerequisites
1. Google Cloud Project set up
2. Docker installed locally
3. gcloud CLI configured
4. GitHub repository connected to Cloud Build

### Deployment Steps

#### 1. Set Up GCP Project
```bash
gcloud projects create echolon-ai --name="Echolon AI Platform"
gcloud config set project echolon-ai
```

#### 2. Enable Required Services
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sql.googleapis.com
gcloud services enable storage.googleapis.com
```

#### 3. Create Secrets
```bash
echo -n "your-database-url" | gcloud secrets create database-url --data-file=-
echo -n "your-secret-key" | gcloud secrets create secret-key --data-file=-
```

#### 4. Deploy Backend
```bash
cd backend
gcloud run deploy echolon-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --memory 1Gi \
  --cpu 1 \
  --allow-unauthenticated \
  --set-env-vars=ENVIRONMENT=production \
  --set-secrets=DATABASE_URL=database-url:latest
```

#### 5. Deploy Frontend
```bash
cd dashboard
gcloud run deploy echolon-dashboard \
  --source . \
  --region us-central1 \
  --platform managed \
  --memory 1Gi \
  --cpu 1 \
  --allow-unauthenticated \
  --set-env-vars=BACKEND_API_URL=https://echolon-backend-xxxxx.run.app
```

## Continuous Deployment

### GitHub Actions Setup
1. Create Workload Identity Provider
2. Configure service account with appropriate permissions
3. Workflows automatically deploy on push to main branch

### Workflow Triggers
- Backend: Changes to `backend/**`
- Frontend: Changes to `dashboard/**`

## Monitoring

### Cloud Run Logs
```bash
gcloud run logs read echolon-backend --region us-central1
gcloud run logs read echolon-dashboard --region us-central1
```

### Cloud Monitoring Dashboards
Set up custom dashboards for:
- Request latency
- Error rates
- CPU and memory usage
- Database connection health

## Scaling

### Automatic Scaling
- Min instances: 0 (scale to zero)
- Max instances: 100 (adjustable)
- Concurrency: 80 requests per instance

## Security

### Best Practices
1. Use Cloud IAM for access control
2. Implement VPC Service Controls
3. Use Secret Manager for sensitive data
4. Enable Cloud Audit Logs
5. Implement rate limiting
6. Use HTTPS only

## Troubleshooting

### Common Issues
1. **Build failures**: Check Cloud Build logs
2. **Runtime errors**: Review Cloud Run logs
3. **Database connection issues**: Verify Cloud SQL proxy connectivity
4. **Timeout errors**: Increase timeout values in gcloud commands

## Rollback Procedure

```bash
# Rollback to previous deployment
gcloud run deploy echolon-backend \
  --image gcr.io/echolon-ai/echolon-backend:previous-sha \
  --region us-central1
```

## Cost Optimization

- Use Cloud Run pay-per-use pricing
- Set minimum instances to 0
- Monitor CPU throttling
- Optimize database queries
- Use CDN for static assets

## References
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Streamlit Cloud Deployment](https://docs.streamlit.io/streamlit-cloud)
