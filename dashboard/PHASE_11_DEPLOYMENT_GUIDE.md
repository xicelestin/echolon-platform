# PHASE 11: PRODUCTION DEPLOYMENT GUIDE

See the complete guide with all files at: https://github.com/xicelestin/echolon-platform

## QUICK START

### 1. Create Dockerfile.api
```bash
cd dashboard
# Copy the Dockerfile.api content from below
```

### 2. Create docker-compose.yml  
```bash
# Copy the docker-compose.yml content from below
```

### 3. Test Locally
```bash
docker-compose up --build
# Dashboard: http://localhost:8080
# API: http://localhost:8000
```

### 4. Deploy to GCP Cloud Run
```bash
gcloud run deploy echolon-dashboard --source .
gcloud run deploy echolon-api --source . -f Dockerfile.api
```

---

## 📦 DOCKER FILES

### Dockerfile.api (FastAPI Backend)
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH PYTHONUNBUFFERED=1
COPY api_gateway.py ml_models/ ml_*.py ./
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/echolon

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=echolon
      - POSTGRES_USER=user  
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 🚀 GCP CLOUD RUN DEPLOYMENT

### Setup GCP
```bash
# Install GCP CLI
curl https://sdk.cloud.google.com | bash

# Login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

### Deploy Dashboard
```bash
cd dashboard
gcloud run deploy echolon-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

### Deploy API
```bash
gcloud run deploy echolon-api \
  --source . \
  --dockerfile Dockerfile.api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

---

## 🔄 GITHUB ACTIONS CI/CD

### Create .github/workflows/deploy.yml
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy Dashboard
        run: |
          cd dashboard
          gcloud run deploy echolon-dashboard \
            --source . \
            --region us-central1
            
      - name: Deploy API  
        run: |
          cd dashboard
          gcloud run deploy echolon-api \
            --source . \
            --dockerfile Dockerfile.api \
            --region us-central1
```

---

## 📊 MONITORING

### GCP Monitoring
- Navigate to Cloud Run → Your Service → Metrics
- Set up alerts for:
  - Response time > 1s
  - Error rate > 1%
  - Memory usage > 80%

---

## 💰 COST ESTIMATE

| Service | Monthly Cost |
|---------|-------------|
| Cloud Run (Dashboard) | $5-15 |
| Cloud Run (API) | $5-15 |
| Cloud SQL (optional) | $7-25 |
| Cloud Storage | $1-5 |
| **Total** | **$18-60/month** |

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Create Dockerfile.api
- [ ] Create docker-compose.yml  
- [ ] Test locally with docker-compose
- [ ] Set up GCP project
- [ ] Deploy to Cloud Run
- [ ] Set up custom domain (optional)
- [ ] Configure GitHub Actions
- [ ] Set up monitoring
- [ ] Load testing
- [ ] Production launch!

---

## 🆘 TROUBLESHOOTING

### Container won't start
```bash
# Check logs
gcloud run services logs read echolon-dashboard

# Test locally
docker build -t test .
docker run -p 8080:8080 test
```

### Out of memory
```bash
# Increase memory
gcloud run services update echolon-dashboard --memory 4Gi
```

---

## 📚 NEXT STEPS

1. **Custom Domain**: Point your domain to Cloud Run
2. **Authentication**: Add auth with Firebase or Auth0
3. **Database**: Set up Cloud SQL for persistent storage
4. **Caching**: Add Redis for performance
5. **CDN**: Use Cloud CDN for static assets

---

**Phase 11 Complete!** 🎉

Your Echolon AI Platform is now production-ready and deployed to the cloud.
