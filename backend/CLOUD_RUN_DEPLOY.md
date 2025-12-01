# 🚀 Echolon AI Backend - Google Cloud Run Deployment Guide

## Overview
This guide walks you through deploying the Echolon AI FastAPI backend to Google Cloud Run - a serverless platform that automatically scales your containerized application.

## Prerequisites

### 1. Google Cloud Account
- Create a free account at https://cloud.google.com/
- **Free tier includes:**
  - 2 million requests per month
  - 360,000 GB-seconds of memory
  - 180,000 vCPU-seconds of compute time

### 2. Install Google Cloud SDK
```bash
# Mac
brew install --cask google-cloud-sdk

# Windows
# Download from: https://cloud.google.com/sdk/docs/install

# Verify installation
gcloud --version
```

### 3. Install Docker
- Mac: https://docs.docker.com/desktop/install/mac-install/
- Windows: https://docs.docker.com/desktop/install/windows-install/

## Quick Deploy (5 Minutes)

### Step 1: Authenticate with Google Cloud
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace PROJECT_ID)
gcloud config set project PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Deploy from GitHub
```bash
# Clone your repository
git clone https://github.com/echolon44/echolon-platform.git
cd echolon-platform/backend

# Deploy to Cloud Run (one command!)
gcloud run deploy echolon-backend \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

### Step 3: Get Your Backend URL
After deployment completes, you'll see:
```
Service [echolon-backend] revision [echolon-backend-00001-xxx] has been deployed.
Service URL: https://echolon-backend-xxxxx-uw.a.run.app
```

**Copy this URL** - you'll need it for your Streamlit dashboard!

## Update Streamlit Dashboard

### Connect Your Backend to Frontend
1. Go to https://share.streamlit.io/
2. Click the three-dot menu next to "echolon-platform"
3. Select **Settings** → **Secrets**
4. Update the `BACKEND_API_URL`:
   ```toml
   BACKEND_API_URL = "https://echolon-backend-xxxxx-uw.a.run.app"
   ```
5. Click **Save changes**

Your dashboard will automatically restart and connect to the backend!

## Environment Variables

### Add Secrets to Cloud Run
```bash
# Set environment variables
gcloud run services update echolon-backend \
  --region us-west1 \
  --set-env-vars="\
ENVIRONMENT=production,\
OPENAI_API_KEY=your-openai-key,\
ANTHROPIC_API_KEY=your-anthropic-key"
```

## Monitoring & Logs

### View Live Logs
```bash
# Stream logs in real-time
gcloud run services logs tail echolon-backend --region us-west1
```

### View in Console
- Go to: https://console.cloud.google.com/run
- Click on **echolon-backend**
- Navigate to **LOGS** tab

## Cost Optimization

### Free Tier Limits
- **Always free:** 2M requests/month
- **Minimal cost:** ~$0-5/month for typical startup usage
- **Auto-scaling:** Scales to zero when not in use (no charges!)

### Monitor Usage
```bash
# Check current billing
gcloud alpha billing accounts list
```

## Troubleshooting

### Common Issues

#### 1. Deployment Fails
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

#### 2. Service Won't Start
```bash
# Check container logs
gcloud run services logs read echolon-backend --region us-west1 --limit=50
```

#### 3. Port Issues
Ensure your Dockerfile exposes port 8080:
```dockerfile
EXPOSE 8080
CMD exec uvicorn main_minimal:app --host 0.0.0.0 --port ${PORT}
```

## Advanced Configuration

### Custom Domain
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service echolon-backend \
  --domain api.echolonai.com \
  --region us-west1
```

### Update Service
```bash
# Redeploy with changes
gcloud run deploy echolon-backend \
  --source . \
  --region us-west1
```

### Scale Configuration
```bash
# Adjust scaling
gcloud run services update echolon-backend \
  --region us-west1 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80
```

## Testing Your Deployment

### Health Check
```bash
# Test health endpoint
curl https://YOUR-SERVICE-URL/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### API Test
```bash
# Test ML forecast endpoint
curl -X POST https://YOUR-SERVICE-URL/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{"data": [100, 120, 115, 130]}'
```

## Next Steps

1. ✅ Deploy backend to Cloud Run
2. ✅ Update Streamlit secrets with backend URL
3. ✅ Test integration
4. 🎯 Share your live dashboard with investors!

## Support Resources

- **Google Cloud Run Docs:** https://cloud.google.com/run/docs
- **Pricing Calculator:** https://cloud.google.com/products/calculator
- **Community Support:** https://stackoverflow.com/questions/tagged/google-cloud-run

---

**Your Complete Stack:**
- 🎨 Frontend: Streamlit Cloud (Free)
- ⚡ Backend: Google Cloud Run (Free Tier)
- 🗄️ Database: PostgreSQL on Cloud SQL (Optional)
- 🤖 AI: OpenAI/Anthropic APIs

**Total Cost:** $0-10/month for early-stage startup! 🚀
