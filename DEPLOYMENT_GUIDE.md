# Echolon Platform - Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the Echolon Platform to production environments. The platform uses Docker, docker-compose, and GCP Cloud Run for containerized deployment.

## Architecture

### Services

1. **FastAPI Backend** (Port 8000)
   - RESTful API for data processing and business logic
   - 4 worker processes for concurrent request handling
   - Health checks every 30 seconds

2. **Streamlit Dashboard** (Port 8501)
   - Interactive web interface for analytics and visualization
   - Real-time data updates via WebSocket
   - Responsive design for mobile and desktop

3. **PostgreSQL Database**
   - Primary data store with persistent volumes
   - Connection pooling: 20 connections with 10 overflow
   - Automatic reconnection and SSL support

4. **Redis Cache**
   - Session management and temporary data storage
   - 3600-second TTL for cached entries
   - Automatic failover and persistence

5. **Nginx Reverse Proxy**
   - Load balancing and request routing
   - SSL/TLS termination
   - Request compression and caching

## Local Development

### Prerequisites

```bash
# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop

# Install Docker Compose (included in Docker Desktop)
# Verify installation
docker --version
docker-compose --version
```

### Running Locally

```bash
# 1. Clone the repository
git clone https://github.com/xicelestin/echolon-platform.git
cd echolon-platform

# 2. Create environment file
cp .env.prod .env.local
# Edit .env.local with your configuration

# 3. Build Docker images
docker-compose build

# 4. Start services
docker-compose up -d

# 5. Check status
docker-compose ps

# 6. View logs
docker-compose logs -f backend
docker-compose logs -f dashboard

# 7. Access services
# Backend API: http://localhost:8000
# Dashboard: http://localhost:8501
# API Docs: http://localhost:8000/docs

# 8. Stop services
docker-compose down
```

## Production Deployment on GCP Cloud Run

### Prerequisites

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate with GCP
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable container.googleapis.com
```

### Deployment Steps

#### 1. Configure Environment Variables

```bash
# Set production environment variables in GitHub Secrets
# Go to: Settings > Secrets and variables > Actions > New repository secret

GCP_PROJECT_ID=your-project-id
GCP_SA_KEY={"type": "service_account", ...}
PROD_API_KEY=your-api-key
PROD_SECRET_KEY=your-secret-key
PROD_DATABASE_URL=postgresql://user:password@host/db
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SLACK_WEBHOOK=https://hooks.slack.com/...
```

#### 2. Push to Main Branch

```bash
# GitHub Actions automatically triggers on push to main
git add .
git commit -m "Deploy production"
git push origin main

# Watch the deployment in:
# GitHub > Actions > CI/CD Pipeline
```

#### 3. Verify Deployment

```bash
# Get the service URL
gcloud run services list

# Test the health endpoint
curl https://echolon-platform-xxxxx.run.app/health

# Check logs
gcloud run services logs read echolon-platform --limit 50
```

### Manual Deployment

If you need to deploy manually:

```bash
# 1. Build Docker image locally
docker build -t echolon-platform:latest .

# 2. Tag for GCP Container Registry
gcloud auth configure-docker
docker tag echolon-platform:latest gcr.io/YOUR_PROJECT_ID/echolon-platform:latest

# 3. Push to registry
docker push gcr.io/YOUR_PROJECT_ID/echolon-platform:latest

# 4. Deploy to Cloud Run
gcloud run deploy echolon-platform \
  --image gcr.io/YOUR_PROJECT_ID/echolon-platform:latest \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL,API_KEY=$API_KEY
```

## Database Setup

### Initial Setup

```bash
# 1. Connect to PostgreSQL
docker-compose exec postgres psql -U echolon -d echolon

# 2. Create tables (run migrations)
python backend/db/migrate.py

# 3. Seed initial data
python backend/db/seed.py
```

### Backup and Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U echolon echolon > backup.sql

# Restore from backup
docker-compose exec postgres psql -U echolon echolon < backup.sql

# Cloud Run backup to Google Storage
gsutil cp gs://echolon-backups/backup.sql .
```

## Monitoring and Logging

### Application Logs

```bash
# Local logs
docker-compose logs -f --tail=100

# Cloud Run logs
gcloud run services logs read echolon-platform

# Structured logging with JSON
cat /app/logs/app.log | jq .
```

### Metrics and Monitoring

- **Prometheus**: Metrics at `/metrics` endpoint
- **Sentry**: Error tracking (configure with SENTRY_DSN)
- **Cloud Monitoring**: GCP built-in monitoring
- **Custom Dashboards**: Grafana setup with Prometheus

### Health Checks

```bash
# API health endpoint
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-01-15T04:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "api": "running"
  }
}
```

## Security Best Practices

1. **Secrets Management**
   - Never commit secrets to version control
   - Use GitHub Secrets for CI/CD
   - Use Google Secret Manager for production

2. **SSL/TLS**
   - Cloud Run automatically provides SSL certificates
   - Use HTTPS for all requests
   - Enable HSTS headers

3. **Access Control**
   - Restrict Cloud Run service account permissions
   - Use VPC connectors for database access
   - Implement API authentication and rate limiting

4. **Data Protection**
   - Enable encryption at rest
   - Enable encryption in transit
   - Regular security audits

## Troubleshooting

### Service Won't Start

```bash
# Check Docker image
docker images

# Check container logs
docker logs container_id

# Rebuild image
docker-compose build --no-cache
```

### Database Connection Issues

```bash
# Test connection
docker-compose exec backend python -c "import psycopg2; conn = psycopg2.connect(...)"

# Check PostgreSQL status
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### Performance Issues

- Monitor CPU and memory usage
- Check database query performance
- Review application logs for errors
- Scale horizontally via Cloud Run concurrency settings

## Scaling and Performance

### Horizontal Scaling

```bash
# Increase Cloud Run instances
gcloud run services update echolon-platform \
  --region us-central1 \
  --max-instances 10 \
  --concurrency 100
```

### Database Scaling

- Upgrade PostgreSQL instance type
- Enable read replicas
- Implement connection pooling

### Caching Strategy

- Use Redis for frequently accessed data
- Implement query caching
- Enable CDN for static assets

## Disaster Recovery

### Backup Schedule

- Daily automated backups to Google Cloud Storage
- Weekly backups retained for 30 days
- Monthly full backups retained for 1 year

### Recovery Procedures

```bash
# Restore from backup
./scripts/restore-backup.sh gs://echolon-backups/backup-2025-01-15.sql

# Test disaster recovery
./scripts/dr-test.sh
```

## Cost Optimization

1. **Cloud Run**
   - Pay only for actual requests
   - Set appropriate memory/CPU
   - Use auto-scaling effectively

2. **Database**
   - Use shared PostgreSQL instance
   - Enable automatic backups
   - Monitor query performance

3. **Storage**
   - Archive old data to Cloud Storage
   - Use compression for backups
   - Delete unused resources

## Support and Documentation

- API Documentation: http://localhost:8000/docs
- GitHub Issues: https://github.com/xicelestin/echolon-platform/issues
- Email: support@echolon-platform.com
- Slack: #echolon-deployment
