# Billing & Persistence Setup

## Stripe (Subscription Billing)

1. Create products in [Stripe Dashboard](https://dashboard.stripe.com/products):
   - **Starter** — $49/month recurring
   - **Growth** — $99/month recurring

2. Copy the **Price IDs** (e.g. `price_xxx`) for each.

3. Add to Streamlit secrets or environment:
   ```
   STRIPE_SECRET_KEY = "sk_live_..."
   STRIPE_PRICE_STARTER_MONTHLY = "price_xxx"
   STRIPE_PRICE_GROWTH_MONTHLY = "price_yyy"
   ```

4. Users click "Subscribe" on Billing page → redirected to Stripe Checkout → return with `session_id` → subscription activated.

## Supabase (Persistent Storage)

For Streamlit Cloud, local files don't persist. Use Supabase:

1. Create project at [supabase.com](https://supabase.com)
2. Run `dashboard/supabase_schema.sql` in SQL Editor
3. Get **Project URL** and **service_role key** from Settings → API
4. Add to Streamlit secrets:
   ```
   SUPABASE_URL = "https://xxx.supabase.co"
   SUPABASE_SERVICE_ROLE_KEY = "eyJ..."
   ```

Sessions and user data will then persist across deploys.

## Tiers

| Tier   | Price  | Data Sources | History | Features                    |
|--------|--------|--------------|---------|-----------------------------|
| Free   | $0     | 1            | 30 days | Executive Briefing only     |
| Starter| $49/mo | 1            | 90 days | + Dashboard, Analytics, Goals|
| Growth | $99/mo | Unlimited    | 12 mo   | All features, exports       |

Default: full access (growth) until Stripe is configured. Set `subscription_tier` in session to enforce limits.
