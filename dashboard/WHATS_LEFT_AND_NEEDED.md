# What's Done vs What's Left — Echolon Platform

## ✅ What's Implemented (No External APIs Required)

| Feature | Status |
|---------|--------|
| **Alerts when metrics deteriorate** | Done — Revenue, margin, ROAS, customers, inventory |
| **Export to PDF** | Done — Requires `reportlab` (in requirements) |
| **Export to Excel** | Done — Requires `openpyxl` (in requirements) |
| **Goals vs actuals** | Done — Progress, gaps, summary |
| **Product/category margins** | Done — When category column exists in data |
| **Inventory alerts** | Done — Low stock, overstock warnings |
| **Stripe API key input** | Done — Paste key in Data Sources → Stripe expander |
| **Mobile layout** | Done — Responsive CSS |
| **Error handling** | Done — User-friendly messages |
| **Driver analysis** | Done — What changed and why |
| **Unified data model** | Done — `utils/data_model.py` |
| **Executive Briefing default** | Done — Landing page |

---

## 🔑 What You Need to Provide

### 1. **Stripe** (when ready)
- **What:** Secret API key (`sk_live_...` or `sk_test_...`)
- **Where:** Stripe Dashboard → Developers → API keys
- **How:** Data Sources → Stripe → Expand "Connect with API Key" → Paste → Connect
- **No code change needed** — UI is ready

### 2. **Shopify** (OAuth)
- **What:** OAuth app credentials + redirect flow
- **Needs:** Shopify Partners app, `shop_url`, `access_token`
- **Code:** `data_source_apis.py` has `fetch_shopify_data()` — add OAuth redirect handler
- **Secrets:** `st.secrets['shopify']['shop_url']`, `st.secrets['shopify']['access_token']`

### 3. **QuickBooks** (OAuth)
- **What:** Intuit Developer app + OAuth
- **Needs:** `company_id`, `access_token`, `refresh_token` (tokens expire)
- **Code:** `data_source_apis.py` has `fetch_quickbooks_data()`
- **Secrets:** In `st.secrets['quickbooks']`

### 4. **Google Sheets**
- **What:** Service account JSON key
- **Needs:** Google Cloud project, Sheets API enabled, share sheet with service account email
- **Code:** `data_source_apis.py` has `fetch_google_sheets_data()`
- **Secrets:** Full JSON in `st.secrets['google_sheets_credentials']`

### 5. **OpenAI / LLM** (optional, for future)
- **Not used today** — All insights are rule-based
- **If you add later:** API key for natural language summaries, chat, or richer explanations

---

## 📋 Integration Requirements Doc

See **`INTEGRATION_REQUIREMENTS.md`** for:
- Exact API endpoints
- Required scopes (Shopify, QuickBooks)
- Secrets format
- Suggested build order

---

## 🚀 Quick Start for Stripe

1. Get Stripe secret key from dashboard.stripe.com
2. Go to Data Sources → Integrations tab
3. Find Stripe card → Expand "Connect with API Key"
4. Paste key → Click "Connect with Key"
5. Data loads; dashboard uses it

No code changes required.
