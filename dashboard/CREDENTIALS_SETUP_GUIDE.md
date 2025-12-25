# API Credentials Setup Guide

This guide explains how to configure credentials for Shopify, Google Sheets, Stripe, and QuickBooks integrations with the Echolon Platform.

## 🛍️ Shopify Setup

### Step 1: Create a Custom App
1. Go to your Shopify Admin Dashboard
2. Navigate to **Settings** → **Apps and integrations** → **Develop apps**
3. Click **Create an app**
4. Enter app name: `Echolon Platform`
5. Set up your app with the following scopes:
   - `read_orders`
   - `read_products`
   - `read_customers`

### Step 2: Get Your Credentials
1. In your app settings, click **Configuration**
2. Copy your **API Key** and **API Secret**
3. Generate an **Admin API access token**
4. Copy the access token (starts with `shpat_`)

### Step 3: Add to `.streamlit/secrets.toml`
```toml
SHOPIFY_STORE_URL = "your-store.myshopify.com"
SHOPIFY_ACCESS_TOKEN = "shpat_your_full_access_token"
SHOPIFY_API_VERSION = "2024-01"
```

---

## 📊 Google Sheets Setup

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project named `Echolon Platform`
3. Enable the **Google Sheets API**
4. Enable the **Google Drive API**

### Step 2: Create a Service Account
1. Go to **Service Accounts** in the Cloud Console
2. Click **Create Service Account**
3. Fill in the details and click **Create and Continue**
4. Grant these roles:
   - `Viewer`
5. Click **Continue** → **Done**

### Step 3: Create and Download JSON Key
1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Click **Create** - this downloads your credentials JSON

### Step 4: Share Your Google Sheet
1. Open your Google Sheet
2. Click **Share**
3. Add the service account email (found in the JSON file under `client_email`)
4. Grant **Viewer** permissions

### Step 5: Add to `.streamlit/secrets.toml`
```toml
GOOGLE_SHEETS_ID = "your-spreadsheet-id-from-url"
GOOGLE_SHEETS_CREDENTIALS = """
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "service-account@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
}
"""
```

---

## 💳 Stripe Setup (Optional)

### Step 1: Get Your API Keys
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Navigate to **Developers** → **API Keys**
3. Copy your **Secret Key** (starts with `sk_`)

### Step 2: Add to `.streamlit/secrets.toml`
```toml
STRIPE_API_KEY = "sk_test_..."
STRIPE_SECRET_KEY = "sk_live_..."
```

---

## 💼 QuickBooks Setup (Optional)

### Step 1: Create a QuickBooks App
1. Go to [Intuit Developer Portal](https://developer.intuit.com/)
2. Create a new app
3. Get your **Client ID** and **Client Secret**
4. Get your **Realm ID** from your QuickBooks company settings

### Step 2: Add to `.streamlit/secrets.toml`
```toml
QUICKBOOKS_CLIENT_ID = "your-client-id"
QUICKBOOKS_CLIENT_SECRET = "your-client-secret"
QUICKBOOKS_REALM_ID = "your-realm-id"
```

---

## 🚀 Streamlit Cloud Deployment

### Step 1: Access Secrets in Streamlit Cloud
1. Go to your Streamlit Cloud app dashboard
2. Click on your app → **Settings**
3. Navigate to **Secrets** tab

### Step 2: Add Each Secret
Copy the entire contents of your `.streamlit/secrets.toml` file and paste it into the Streamlit Cloud secrets editor.

**Important:** Never commit `.streamlit/secrets.toml` to GitHub. Add it to `.gitignore`:
```bash
echo ".streamlit/secrets.toml" >> .gitignore
```

---

## ✅ Testing Your Configuration

Once credentials are set up, test by:
1. Running `streamlit run app.py` locally
2. Navigating to the "Connect Your Data Sources" page
3. Clicking "Connect" for Shopify or Google Sheets
4. Verifying that real data loads successfully

---

## 🔒 Security Best Practices

✅ **Do:**
- Store credentials in `.streamlit/secrets.toml` locally
- Add secrets to Streamlit Cloud via the UI
- Use API keys with minimal required permissions
- Rotate keys regularly

❌ **Don't:**
- Commit secrets.toml to Git
- Share API keys in messages or chat
- Use personal credentials for production
- Hardcode credentials in the code

---

## 🆘 Troubleshooting

### "Authentication Failed" for Shopify
- Verify the store URL format: `your-store.myshopify.com` (not HTTPS)
- Check that the access token hasn't expired
- Ensure the custom app has the required scopes

### "Permission Denied" for Google Sheets
- Verify you've shared the sheet with the service account email
- Check that the service account has at least "Viewer" permissions
- Verify the Spreadsheet ID is correct

### Secrets Not Loading
- Restart the Streamlit app: `streamlit run app.py`
- Verify the `.streamlit/` folder path is in the `dashboard` directory
- Check for TOML syntax errors in secrets.toml

---

## 📚 Additional Resources

- [Shopify Admin API Docs](https://shopify.dev/api/admin-rest)
- [Google Sheets API Docs](https://developers.google.com/sheets/api)
- [Stripe API Docs](https://stripe.com/docs/api)
- [QuickBooks API Docs](https://developer.intuit.com/docs)
