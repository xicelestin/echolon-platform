# Infrastructure Overview - Echolon AI Platform

## Google Cloud Platform (GCP) Resources

### Compute
- **Cloud Run**: Serverless container runtime for backend and frontend
  - Backend Service: echolon-backend (1 CPU, 1 GB RAM)
  - Frontend Service: echolon-dashboard (1 CPU, 1 GB RAM)
  - Auto-scaling: 0-100 instances
  - Deployment: From Docker images in GCR

### Storage
- **Cloud SQL**: Managed PostgreSQL database
  - Instance: PostgreSQL 13+
  - Storage: 10 GB (auto-scaling)
  - Backups: Automated daily
  - Availability: High availability replica in different zone

- **Cloud Storage**: Object storage for file uploads
  - Bucket: echolon-ai-uploads
  - Access: Private with IAM controls
  - Versioning: Enabled
  - Lifecycle: Archive after 90 days

### Networking
- **Cloud Load Balancing**: Distribute traffic
  - Load Balancer Type: HTTP(S)
  - SSL Certificate: Managed by GCP
  - Health Checks: Every 10 seconds

### Security & Identity
- **Cloud IAM**: Identity and access management
  - Service Accounts: GitHub Actions, Cloud Run services
  - Roles: Custom roles for least privilege

- **Secret Manager**: Secure credential storage
  - Secrets: DATABASE_URL, SECRET_KEY, API_KEYS
  - Rotation: Manual or automatic
  - Access: Restricted to authorized services

- **Cloud Armor**: DDoS protection
  - Rules: Rate limiting, geo-blocking
  - Logging: All requests logged

### Monitoring & Logging
- **Cloud Logging**: Centralized log management
  - Sink: Export to Cloud Storage for long-term retention
  - Log levels: INFO, WARNING, ERROR
  - Retention: 30 days in Cloud Logging

- **Cloud Monitoring**: Performance monitoring
  - Metrics: CPU, Memory, Request latency
  - Alerts: Email notifications for critical issues
  - Custom dashboards: Application-specific metrics

- **Cloud Trace**: Distributed tracing
  - Trace sampling: 10% of requests
  - Latency analysis: Identify bottlenecks

### CI/CD Pipeline
- **GitHub Actions**: Automated deployment
  - Trigger: Push to main branch
  - Workflow 1: Backend deployment
  - Workflow 2: Frontend deployment

- **Cloud Build**: Alternate build option
  - Docker builds: Multi-stage optimization
  - Image registry: Google Container Registry (GCR)

## Infrastructure as Code (IaC)

### Terraform Configuration (Optional)
```hcl
# Example structure
resource "google_cloud_run_service" "backend" {
  name     = "echolon-backend"
  location = "us-central1"
  template {
    spec {
      containers {
        image = "gcr.io/project-id/echolon-backend:latest"
        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }
    }
  }
}
```

## Deployment Process

### Manual Deployment
```bash
# Setup GCP project
gcloud config set project PROJECT_ID

# Deploy backend
cd backend
gcloud run deploy echolon-backend \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --allow-unauthenticated

# Deploy frontend
cd ../dashboard
gcloud run deploy echolon-dashboard \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --allow-unauthenticated
```

### Automated Deployment (GitHub Actions)
1. Developer pushes code to main branch
2. GitHub Actions workflow triggered
3. Docker image built and tested
4. Image pushed to GCR
5. Cloud Run service updated
6. Health checks verify deployment

## Cost Optimization

### Strategies
- **Cloud Run**: Pay-per-request pricing
- **Minimum Instances**: Set to 0 for zero cost when idle
- **Scheduled Scaling**: Higher instances during business hours
- **Caching**: Redis for session data (optional)
- **CDN**: CloudCDN for static asset delivery

### Estimated Monthly Costs
- Cloud Run (backend + frontend): $50-200
- Cloud SQL: $100-150
- Cloud Storage: $5-20
- Cloud Logging: $10-30
- **Total**: $165-400 (depending on usage)

## Disaster Recovery

### Backup Strategy
- **Database**: Automated daily backups
- **Code**: Versioned in GitHub
- **Configuration**: Stored in Secret Manager
- **Recovery Time**: < 1 hour for full restore

### High Availability
- **Cloud Run**: Multi-zone deployment
- **Cloud SQL**: High availability replica
- **Load Balancing**: Automatic failover
- **SLA**: 99.9% uptime (Cloud Run managed)

## Scaling Configuration

### Horizontal Scaling
```yaml
Cloud Run:
  min_instances: 0
  max_instances: 100
  concurrency: 80
  timeout: 3600 seconds

Cloud SQL:
  max_connections: 100
  connection_pool: 10
```

## Security Checklist

- [x] VPC Service Controls enabled
- [x] Cloud Armor DDoS protection active
- [x] Secret Manager for all credentials
- [x] IAM roles follow least privilege
- [x] SSL/TLS for all traffic
- [x] Firewall rules restrict access
- [x] Audit logging enabled
- [x] Regular security scans scheduled

## Maintenance Windows

- **Cloud SQL Maintenance**: Monday 2-4 AM UTC
- **Cloud Run Updates**: Automatic, zero-downtime
- **Certificate Renewal**: Automatic
- **Security Patches**: Applied within 7 days

## Monitoring Alerts

### Critical Alerts
- Error rate > 5%
- Request latency > 2 seconds (p95)
- Database CPU > 80%
- Disk space > 90%
- Service unavailable

### Action Response
1. Alert sent via email
2. Automatic logs collected
3. On-call engineer notified
4. Investigation initiated
5. Incident resolution tracked

## Contact & Escalation

- **Primary Support**: Engineering team
- **Escalation**: Platform lead
- **On-Call**: Rotation schedule in PagerDuty
- **Status Page**: https://status.echolon.ai

## Additional Resources

- [GCP Documentation](https://cloud.google.com/docs)
- [Cloud Run Guide](https://cloud.google.com/run/docs)
- [Deployment Guide](./deployment.md)
- [Architecture](./architecture.md)
