# Echolon Setup Checklist

Complete these steps to go live. **I'll need from you:** API keys, URLs, and any credentials marked below.

---

## 1. Stripe (Billing)

### You need to provide:
- [ ] **STRIPE_SECRET_KEY** — From [Stripe Dashboard](https://dashboard.stripe.com/apikeys) → Secret key (starts with `sk_live_` or `sk_test_`)
- [ ] **STRIPE_PRICE_STARTER_MONTHLY** — Create product "Starter" ($49/mo), copy Price ID (e.g. `price_xxx`)
- [ ] **STRIPE_PRICE_GROWTH_MONTHLY** — Create product "Growth" ($99/mo), copy Price ID

### Where to add:
- **Streamlit Cloud:** App → Settings → Secrets
- **Local:** `dashboard/.streamlit/secrets.toml`

### Format (secrets.toml):
```toml
STRIPE_SECRET_KEY = "sk_live_..."
STRIPE_PRICE_STARTER_MONTHLY = "price_xxx"
STRIPE_PRICE_STARTER_ANNUAL = "price_xxx"
STRIPE_PRICE_GROWTH_MONTHLY = "price_xxx"
STRIPE_PRICE_GROWTH_ANNUAL = "price_xxx"
```

### Optional — Stripe Webhook (for subscription lifecycle):
If you deploy the backend (e.g. Cloud Run):
1. Add webhook in Stripe Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://your-backend-url/api/v1/stripe/webhook`
3. Events: `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
4. Copy the **Signing secret** (whsec_...) and set `STRIPE_WEBHOOK_SECRET` in your backend env

---

## 2. User Accounts

### You need to provide:
- [ ] **Username(s)** and **password(s)** for each user

### How to add users:
1. Generate password hash:
   ```python
   from auth import generate_password_hash
   print(generate_password_hash("your_password"))
   ```
2. Add to secrets:
   ```toml
   [users]
   your_username = "sha256_hash_from_step_1"
   ```

### Where to add:
Same as Stripe — Streamlit secrets or `dashboard/.streamlit/secrets.toml`

---

## 3. Supabase (Data Persistence on Streamlit Cloud)

*Required if deploying to Streamlit Cloud — otherwise data resets on redeploy.*

### You need to provide:
- [ ] **SUPABASE_URL** — From [Supabase](https://supabase.com) project → Settings → API → Project URL
- [ ] **SUPABASE_SERVICE_ROLE_KEY** — Same page → service_role key (keep secret!)

### What you do:
1. Create project at supabase.com
2. Run `dashboard/supabase_schema.sql` in SQL Editor
3. Add URL and key to Streamlit secrets

### Format:
```toml
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJ..."
```

---

## 4. Production Mode

### You do:
- [ ] In Streamlit Cloud: Add secret `ECHOLON_PRODUCTION = "true"` (disables demo login)
- [ ] Or set env var `ECHOLON_PRODUCTION=true` where you deploy

---

## 5. Optional Integrations

### Stripe (Data Source)
Users paste their own Stripe key in the app — no config needed from you.

### Google Sheets
- [ ] **GOOGLE_SHEETS_CREDENTIALS** — JSON from Google Cloud service account (see `dashboard/CREDENTIALS_SETUP_GUIDE.md`)

### Shopify / QuickBooks
Marked "Coming Soon" — OAuth not yet implemented.

---

## Quick Reference: Full secrets.toml Example

See `dashboard/.streamlit/secrets.example.toml` for a copy-paste template.

```toml
# Billing
STRIPE_SECRET_KEY = "sk_live_..."
STRIPE_PRICE_STARTER_MONTHLY = "price_xxx"
STRIPE_PRICE_GROWTH_MONTHLY = "price_yyy"

# Users (hash from generate_password_hash)
[users]
admin = "abc123..."
demo = "def456..."

# Supabase (for Streamlit Cloud)
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJ..."

# Production
ECHOLON_PRODUCTION = "true"
```

---

## Summary: What I Need From You

| Item | Where to get it | Add to |
|------|-----------------|--------|
| Stripe Secret Key | Stripe Dashboard → API Keys | Streamlit secrets |
| Stripe Price IDs (Starter, Growth) | Stripe Dashboard → Products | Streamlit secrets |
| Username + password hash | Run `generate_password_hash` in Python | Streamlit secrets `[users]` |
| Supabase URL + Key | supabase.com project | Streamlit secrets |
| ECHOLON_PRODUCTION | Set to "true" | Streamlit secrets |

Once you have these, add them to your Streamlit Cloud app secrets and you're good to go.
