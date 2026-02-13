# Environment Variables Reference

## Overview

This document describes all environment variables used by the Echolon AI backend application.

## Required Variables

### PORT
- **Description**: Port number for the application to listen on
- **Default**: 8080
- **Cloud Run**: Automatically set by Cloud Run
- **Local Dev**: Can be overridden
- **Example**: `PORT=8080`

### LOG_LEVEL
- **Description**: Logging verbosity level
- **Default**: info
- **Options**: debug, info, warning, error, critical
- **Example**: `LOG_LEVEL=info`

## Optional Variables

### ALLOWED_ORIGINS
- **Description**: CORS allowed origins (comma-separated). Use `*` for dev only.
- **Example**: `ALLOWED_ORIGINS=http://localhost:8501,https://app.echolon.ai`

### MAX_CSV_BYTES, MAX_CSV_ROWS
- **Description**: CSV upload limits (default: 10MB, 100k rows)
- **Example**: `MAX_CSV_BYTES=10485760` `MAX_CSV_ROWS=100000`

### DEFAULT_USER_ID
- **Description**: Fallback user_id when auth not configured (default: 1)

### DATABASE_URL
- **Description**: PostgreSQL database connection string
- **Format**: `postgresql://user:password@host:port/database`
- **Cloud Run**: Set via Secret Manager
- **Example**: `DATABASE_URL=postgresql://user:pass@localhost:5432/echolon`
- **Note**: Not required for minimal deployment

### PYTHONUNBUFFERED
- **Description**: Enable unbuffered Python output for real-time logging
- **Default**: 1 (enabled)
- **Options**: 0 (buffered), 1 (unbuffered)
- **Example**: `PYTHONUNBUFFERED=1`
- **Note**: Should always be 1 for Cloud Run

## Cloud Run Specific

### Automatically Set by Cloud Run

These variables are automatically configured by Cloud Run:

- `PORT`: Container port (always 8080 by default)
- `K_SERVICE`: Service name
- `K_REVISION`: Revision name
- `K_CONFIGURATION`: Configuration name

### Set in Deployment

Configured in `.github/workflows/backend-deploy.yml`:

```yaml
--update-env-vars=DATABASE_URL=${{ secrets.DATABASE_URL }},LOG_LEVEL=info
```

## Local Development

### .env File Example

Create a `.env` file in the backend directory:

```bash
# Application
PORT=8080
LOG_LEVEL=debug

# Python
PYTHONUNBUFFERED=1

# Database (optional)
DATABASE_URL=postgresql://postgres:password@localhost:5432/echolon_dev
```

### Loading Environment Variables

```bash
# Using python-dotenv
from dotenv import load_dotenv
load_dotenv()

# Using export
export $(cat .env | xargs)

# Using source
source .env
```

## Verification

### Check Environment Variables

```bash
# In container
echo $PORT
echo $LOG_LEVEL
echo ${DATABASE_URL:+***set***}  # Shows ***set*** if variable exists

# Via Python
import os
print(f"PORT: {os.getenv('PORT', '8080')}")
print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL', 'info')}")
```

### Cloud Run Service Variables

```bash
# View current environment variables
gcloud run services describe echolon-api --region=us-west1 --format="value(spec.template.spec.containers[0].env)"

# Update environment variable
gcloud run services update echolon-api \
  --region=us-west1 \
  --update-env-vars=LOG_LEVEL=debug
```

## Security Best Practices

1. **Never commit secrets to git**
   - Use `.gitignore` for `.env` files
   - Use Secret Manager for production

2. **Use Secret Manager for sensitive data**
   ```bash
   gcloud secrets create DATABASE_URL --data-file=-
   ```

3. **Rotate secrets regularly**
   - Update database passwords
   - Regenerate API keys

4. **Minimum privilege**
   - Only grant necessary permissions
   - Use service accounts

## Troubleshooting

### Variable Not Set
```bash
# Check if variable exists
if [ -z "$PORT" ]; then
  echo "PORT not set"
fi
```

### Wrong Value
```bash
# Debug environment
env | grep -E '(PORT|LOG_LEVEL|DATABASE)'
```

### Cloud Run Issues
```bash
# View logs for environment issues
gcloud run services logs read echolon-api --limit=50 | grep -i "env"
```

---

*Last Updated: 2025-11-30*
