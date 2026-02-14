# Echolon Platform

AI-powered business intelligence for SMBs. FastAPI backend + Streamlit dashboard.

## Quick Start

```bash
# Dashboard (main app)
cd dashboard && pip install -r requirements.txt && streamlit run app.py

# Backend API (optional)
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
```

## Structure

```
├── dashboard/     # Streamlit app (Executive Briefing, Analytics, Data Sources, etc.)
├── backend/       # FastAPI API + ML services
├── docs/          # Architecture, deployment, troubleshooting
└── infra/         # CI/CD, deployment configs
```

## Docs

- [Quick Start](QUICK_START.md) — Full setup guide
- [Deployment](DEPLOYMENT_GUIDE.md) — Deploy to Cloud Run, Streamlit Cloud
- [Dashboard Credentials](dashboard/CREDENTIALS_SETUP_GUIDE.md) — Stripe, Shopify, Google Sheets
