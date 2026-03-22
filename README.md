# Echolon Platform

AI-powered business intelligence for SMBs. FastAPI backend + Streamlit dashboard.

**License:** [MIT](LICENSE) · **Security:** [SECURITY.md](SECURITY.md) · **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## Quick Start

```bash
# Dashboard (main app)
cd dashboard && pip install -r requirements.txt && streamlit run app.py

# Backend API (optional)
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
```

## CI & quality

- **[`.github/workflows/ci.yml`](.github/workflows/ci.yml)** — on each PR/push to `main` / `develop`: dashboard `pytest`, backend `smoke_test.py`, `compileall`.
- **[`docs/TESTING.md`](docs/TESTING.md)** — local testing and venv tips.
- **Dependabot** — weekly pip + GitHub Actions updates (see [`.github/dependabot.yml`](.github/dependabot.yml)).
- **Optional:** `pip install pre-commit && pre-commit install` — see [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

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
- [Session state keys](dashboard/docs/SESSION_STATE.md) — `st.session_state` reference for contributors
