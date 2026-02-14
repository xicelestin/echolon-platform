# Echolon AI Dashboard

AI-powered business intelligence platform built with Streamlit for SMBs.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
dashboard/
├── app.py                 # Main app, auth, routing
├── auth.py                # Login, landing page, session
├── data_source_apis.py    # Stripe, Shopify, Google Sheets, QuickBooks
├── pages_*.py             # Page modules (Executive Briefing, Analytics, etc.)
├── components/            # Charts, metrics, UI components
├── utils/                 # Metrics, export, sync, industry benchmarks
└── requirements.txt
```

## Key Pages

- **Executive Briefing** — Do This Week, cash flow, top opportunities
- **Data Sources** — CSV upload, Stripe, Shopify, Google Sheets
- **Analytics, Insights, Predictions** — Data-driven views
- **Goals** — Set and track business targets

## Configuration

- **Credentials:** See `CREDENTIALS_SETUP_GUIDE.md` for Stripe, Shopify, Google Sheets
- **Streamlit secrets:** Add to `.streamlit/secrets.toml` or Streamlit Cloud dashboard
- **Demo login:** `demo` / `demo123` (disable with `ECHOLON_PRODUCTION=true`)

## Deployment

Deploy to [Streamlit Cloud](https://share.streamlit.io): connect repo, set main file to `dashboard/app.py`, add secrets.
