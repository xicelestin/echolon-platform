# Echolon Integration Requirements

What you need to connect each data source. Build these incrementally — CSV upload works today.

---

## ✅ CSV Upload (Functional Today)

**No API required.** Users upload a CSV file and map columns.

**Required columns:** `date`, `revenue`, `orders`  
**Optional (for driver analysis):** `channel`, `category`, `product`, `customers`, `cost`

**Location:** Data Sources → CSV Upload

---

## 🛍️ Shopify

**API:** Shopify Admin API  
**Auth:** OAuth 2.0 (or Custom App with Admin API access token)

**What you need:**
1. **Shop URL** — e.g. `your-store.myshopify.com`
2. **Access Token** — From Shopify Admin → Settings → Apps and sales channels → Develop apps → Create app → Configure Admin API scopes

**Required scopes:**
- `read_orders`
- `read_customers`
- `read_products` (optional, for product-level driver analysis)

**Endpoints used:**
- `GET /admin/api/2024-01/orders.json` — Orders with `created_at_min` for date range

**Code location:** `data_source_apis.py` → `fetch_shopify_data()`

**Secrets (Streamlit):**
```toml
[shopify]
shop_url = "your-store.myshopify.com"
access_token = "shpat_xxxxx"
```

---

## 💼 QuickBooks Online

**API:** QuickBooks Online API v3  
**Auth:** OAuth 2.0

**What you need:**
1. **Intuit Developer Account** — developer.intuit.com
2. **App credentials** — Client ID, Client Secret
3. **Company ID** — From OAuth flow
4. **Access Token + Refresh Token** — From OAuth flow (tokens expire; refresh required)

**Endpoints used:**
- `GET /v3/company/{companyId}/query` — Query Invoice, SalesReceipt for revenue

**Code location:** `data_source_apis.py` → `fetch_quickbooks_data()`

**Secrets:**
```toml
[quickbooks]
company_id = "1234567890"
access_token = "xxxxx"
refresh_token = "xxxxx"
```

---

## 💳 Stripe

**API:** Stripe API  
**Auth:** Secret API Key (sk_live_xxx or sk_test_xxx)

**What you need:**
1. **Stripe Account** — stripe.com
2. **Secret Key** — Dashboard → Developers → API keys

**Endpoints used:**
- `Charge.list()` or `PaymentIntent.list()` — Transactions

**Code location:** `data_source_apis.py` → `fetch_stripe_data()`

**Install:** `pip install stripe`

**Secrets:**
```toml
[stripe]
api_key = "sk_live_xxxxx"
```

---

## 📊 Google Sheets

**API:** Google Sheets API  
**Auth:** Service Account (for server-to-server) or OAuth (for user's sheets)

**What you need:**
1. **Google Cloud Project** — console.cloud.google.com
2. **Enable Sheets API + Drive API**
3. **Service Account** — Create credentials → Service account → JSON key
4. **Share the sheet** with the service account email (viewer access)

**Code location:** `data_source_apis.py` → `fetch_google_sheets_data()`

**Install:** `pip install gspread google-auth`

**Secrets:**
```toml
[google_sheets_credentials]
# Paste full JSON from service account key file
type = "service_account"
project_id = "xxx"
private_key_id = "xxx"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "xxx@xxx.iam.gserviceaccount.com"
client_id = "xxx"
```

---

## 🔌 Connection Flow (Data Sources Page)

1. User clicks "Connect" on a source
2. **OAuth sources (Shopify, QuickBooks):** Redirect to provider → callback with code → exchange for tokens → store in session/secrets
3. **API key sources (Stripe):** User pastes key or it's read from secrets
4. Call `fetch_data_from_api(source_key, credentials)`
5. Normalize result via `utils/data_model.normalize_to_canonical()`
6. Store in `st.session_state.uploaded_data`

**Router:** `data_source_apis.py` → `fetch_data_from_api()`

---

## 📋 Canonical Data Model

All sources normalize to this schema (see `utils/data_model.py`):

| Column | Required | Purpose |
|--------|----------|---------|
| date | Yes | Time dimension |
| revenue | Yes | Primary metric |
| orders | Recommended | Volume |
| customers | Optional | Retention analysis |
| profit, profit_margin | Optional | Profitability |
| marketing_spend, roas | Optional | Marketing efficiency |
| channel | Optional | **Driver analysis** — what channel drove change |
| category, product | Optional | **Driver analysis** — product/category attribution |

---

## Next Steps (Build Order)

1. **CSV with channel** — Already supported. Users can map channel column.
2. **Stripe** — Easiest API (single key). Add "Paste API key" UI.
3. **Shopify** — OAuth flow + store credentials. High value for e-commerce.
4. **QuickBooks** — OAuth + token refresh. Critical for SMB accounting.
5. **Google Sheets** — Service account. Good for spreadsheets users.
