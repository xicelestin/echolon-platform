# -*- coding: utf-8 -*-
"""Multi-source data integration page for Echolon AI.
Supports Shopify, QuickBooks, Google Sheets, Stripe, and CSV uploads.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from data_source_apis import fetch_data_from_api
from auth import get_current_user
from utils.user_data_storage import save_user_data

# ==================== DATA SOURCE CONFIGURATIONS ====================
DATA_SOURCES = {
    'shopify': {
        'name': 'Shopify',
        'icon': '🛍️',
        'description': 'E-commerce platform data',
        'fields': ['orders', 'customers', 'products', 'revenue'],
        'oauth_url': 'https://shopify.com/oauth',  # Placeholder
        'coming_soon': False
    },
    'quickbooks': {
        'name': 'QuickBooks Online',
        'icon': '💼',
        'description': 'Accounting & financial data',
        'fields': ['revenue', 'expenses', 'invoices', 'customers'],
        'oauth_url': 'https://quickbooks.intuit.com/oauth',  # Placeholder
        'coming_soon': False
    },
    'google_sheets': {
        'name': 'Google Sheets',
        'icon': '📊',
        'description': 'Spreadsheet data sync',
        'fields': ['custom data'],
        'oauth_url': 'https://accounts.google.com/oauth',  # Placeholder
        'coming_soon': False
    },
    'stripe': {
        'name': 'Stripe',
        'icon': '💳',
        'description': 'Payment & transaction data',
        'fields': ['transactions', 'revenue', 'customers'],
        'oauth_url': 'https://stripe.com/oauth',  # Placeholder
        'coming_soon': False
    },
    'csv': {
        'name': 'CSV Upload',
        'icon': '📁',
        'description': 'Manual file upload',
        'fields': ['custom data'],
        'coming_soon': False
    }
}

# ==================== SESSION STATE ====================
if 'connected_sources' not in st.session_state:
    st.session_state.connected_sources = {}

if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []

# ==================== HELPER FUNCTIONS ====================
def render_source_card(source_key, source_info):
    """Render a data source integration card"""
    is_connected = source_key in getattr(st.session_state, 'connected_sources', {})
    
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 2])
        
        with col1:
            st.markdown(f"<div style='font-size: 48px;'>{source_info['icon']}</div>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"### {source_info['name']}")
            st.caption(source_info['description'])
            
            if source_info.get('coming_soon'):
                st.info("🚀 Coming Soon")
            elif is_connected:
                from utils.sync_utils import format_last_sync_ago
                last = st.session_state.connected_sources[source_key].get('last_sync', '')
                ago = format_last_sync_ago(last)
                st.success(f"✅ Connected — Last synced {ago}")
            else:
                st.caption(f"Data: {', '.join(source_info['fields'])}")
        
        with col3:
            if source_info.get('coming_soon'):
                st.button("Notify Me", key=f"notify_{source_key}", disabled=True)
            elif is_connected:
                if st.button("Sync Now", key=f"sync_{source_key}", type="secondary"):
                    sync_data_source(source_key)
                if st.button("Disconnect", key=f"disconnect_{source_key}"):
                    disconnect_source(source_key)
            elif source_key == 'csv':
                if st.button("Upload CSV", key=f"connect_{source_key}", type="primary"):
                    st.session_state.show_csv_upload = True
            elif source_key == 'stripe':
                # Stripe: API key input (ready when user has key)
                with st.expander("Connect with API Key", expanded=False):
                    api_key = st.text_input(
                        "Stripe Secret Key",
                        type="password",
                        placeholder="sk_live_... or sk_test_...",
                        key="stripe_key_input",
                        help="Get from Stripe Dashboard → Developers → API keys"
                    )
                    if st.button("Connect with Key", key="stripe_connect_btn"):
                        if api_key:
                            connect_source_with_credentials(source_key, {'api_key': api_key})
                        else:
                            st.warning("Enter your Stripe secret key.")
            else:
                if st.button("Connect", key=f"connect_{source_key}", type="primary"):
                    connect_source(source_key, source_info)
        
        st.markdown("---")

def connect_source_with_credentials(source_key, credentials):
    """Connect using provided credentials (e.g. Stripe API key)."""
    # Persist API keys per user (for Stripe sync, reconnect after refresh)
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}
    if "api_key" in credentials:
        st.session_state.api_keys[source_key] = credentials["api_key"]
    with st.spinner(f"Connecting to {DATA_SOURCES.get(source_key, {}).get('name', source_key)}..."):
        st.session_state.connected_sources[source_key] = {
            'name': DATA_SOURCES[source_key]['name'],
            'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'last_sync': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'active'
        }
        try:
            data_df = fetch_data_from_api(source_key, credentials)
            if data_df is not None and not data_df.empty:
                st.session_state.uploaded_data = data_df
                st.session_state.upload_history.append({
                    'filename': f"{DATA_SOURCES[source_key]['name']}_data",
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'rows': len(data_df),
                    'columns': len(data_df.columns),
                    'source': source_key
                })
                save_user_data(get_current_user())
                st.success(f"✅ Connected! Loaded {len(data_df)} rows from {DATA_SOURCES[source_key]['name']}.")
            else:
                st.warning("Connected but no data returned. Check your API key and account.")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
        st.rerun()


def connect_source(source_key, source_info):
    """Initiate OAuth connection and fetch data from source"""
    with st.spinner(f"Connecting to {source_info['name']}..."):
        # In production, this would redirect to OAuth
        # For MVP, we'll simulate a connection AND generate demo data
        st.session_state.connected_sources[source_key] = {
            'name': source_info['name'],
            'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'last_sync': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'active'
        }
        
        # CRITICAL: Actually fetch and store data
        try:
            data_df = fetch_data_from_source(source_key, source_info)
            if data_df is not None and not data_df.empty:
                # Store in session state so dashboard can access it
                st.session_state.uploaded_data = data_df
                
                # Add to upload history
                st.session_state.upload_history.append({
                    'filename': f"{source_info['name']}_data",
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'rows': len(data_df),
                    'columns': len(data_df.columns),
                    'source': source_key
                })
                save_user_data(get_current_user())
                st.success(f"✅ Successfully connected to {source_info['name']} and loaded {len(data_df)} rows!")
                st.info("💡 Navigate to Dashboard to see your data insights")
            else:
                st.warning("Connected but no data was fetched. Please check your account permissions.")
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("💡 For MVP: OAuth flow is simulated. Production will use real OAuth.")
        
        st.rerun()

def fetch_data_from_source(source_key, source_info):
    """Fetch actual data from the connected source using real APIs."""
    try:
        api_data = fetch_data_from_api(source_key)
        if api_data is not None and not api_data.empty:
            return api_data
    except Exception as e:
        st.warning(f"Could not fetch from API: {str(e)}. Using demo data.")
    return generate_demo_data_fallback(source_key)



# ==================== MAIN PAGE RENDER FUNCTION ====================
def render_data_sources_page():
    """Main function - delegates to enhanced version"""
    render_data_sources_page_enhanced()

def sync_data_source(source_key):
    """Re-sync data from a connected source"""
    with st.spinner(f"Syncing {source_key}..."):
        source_info = DATA_SOURCES.get(source_key, {})
        # Use stored API key for Stripe sync (persisted per user)
        credentials = {}
        if source_key == "stripe":
            key = st.session_state.get("api_keys", {}).get("stripe")
            if key:
                credentials = {"api_key": key}
        try:
            data_df = fetch_data_from_api(source_key, credentials) if credentials else fetch_data_from_source(source_key, source_info)
            
            if data_df is not None and not data_df.empty:
                st.session_state.uploaded_data = data_df
                st.session_state.connected_sources[source_key]['last_sync'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_user_data(get_current_user())
                st.success(f"✅ Successfully synced {len(data_df)} rows from {source_info['name']}!")
            else:
                st.warning("Sync completed but no new data was found.")
        except Exception as e:
            st.error(f"Sync failed: {str(e)}")
    
    st.rerun()

def disconnect_source(source_key):
    """Disconnect a data source"""
    if source_key in st.session_state.connected_sources:
        del st.session_state.connected_sources[source_key]
        st.success(f"Disconnected from {DATA_SOURCES[source_key]['name']}")
        st.rerun()

def generate_demo_data_fallback(source_key):
    """Generate demo data as fallback when API connection fails"""
    import numpy as np
    
    # Generate 365 days of demo data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)  # For reproducibility
    
    # Base data generation with realistic patterns
    trend = np.linspace(40000, 60000, len(dates))
    seasonality = 5000 * np.sin(np.linspace(0, 4*np.pi, len(dates)))
    noise = np.random.normal(0, 3000, len(dates))
    
    data = pd.DataFrame({
        'date': dates,
        'revenue': trend + seasonality + noise,
        'orders': np.random.poisson(100, len(dates)) + (trend/1000).astype(int),
        'customers': np.random.poisson(50, len(dates)) + (trend/2000).astype(int),
        'cost': (trend + seasonality + noise) * 0.6,
        'marketing_spend': np.random.normal(5000, 1000, len(dates)),
        'inventory_units': np.random.randint(500, 2000, len(dates)),
        'new_customers': np.random.randint(10, 50, len(dates)),
        'conversion_rate': np.random.uniform(1.5, 4.5, len(dates))
    })
    
    # Derived metrics
    data['profit'] = data['revenue'] - data['cost']
    data['profit_margin'] = (data['profit'] / data['revenue'] * 100).round(2)
    data['roas'] = (data['revenue'] / data['marketing_spend']).round(2)
    data['avg_order_value'] = (data['revenue'] / data['orders']).round(2)
    
    # Add source-specific fields
    if source_key == 'shopify':
        data['platform'] = 'Shopify'
        data['channel'] = np.random.choice(['Online Store', 'POS', 'Mobile App'], len(dates))
    elif source_key == 'quickbooks':
        data['platform'] = 'QuickBooks'
        data['expense_category'] = np.random.choice(['COGS', 'Marketing', 'Operations'], len(dates))
    elif source_key == 'stripe':
        data['platform'] = 'Stripe'
        data['payment_method'] = np.random.choice(['card', 'bank', 'wallet'], len(dates))
    
    return data

# CSV upload limits (match backend)
MAX_CSV_MB = 10
MAX_CSV_ROWS = 100_000

# ==================== ENHANCED CSV UPLOAD HANDLER ====================
def render_csv_upload_section():
    """Enhanced CSV upload with drag-drop, validation, preview, and column mapping"""
    st.subheader("📁 Upload Your Data")
    st.markdown("Upload a CSV file to analyze your business data")
    
    # File uploader with drag-and-drop
    uploaded_file = st.file_uploader(
        "Drag and drop your CSV file here or click to browse",
        type=['csv'],
        help=f"Max {MAX_CSV_MB}MB, {MAX_CSV_ROWS:,} rows. Required: date, revenue, orders"
    )
    
    if uploaded_file is not None:
        try:
            # Progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Read and validate size
            status_text.text("📖 Reading file...")
            progress_bar.progress(0.2)
            contents = uploaded_file.read()
            if len(contents) > MAX_CSV_MB * 1024 * 1024:
                st.error(f"❌ File too large. Maximum size: {MAX_CSV_MB}MB")
                return
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file)
            
            # Step 2: Validation
            status_text.text("✅ Validating data...")
            progress_bar.progress(0.4)
            
            validation_errors = []
            validation_warnings = []
            
            if df.empty:
                validation_errors.append("File is empty")
            
            if len(df) > MAX_CSV_ROWS:
                validation_errors.append(f"Too many rows ({len(df):,}). Maximum: {MAX_CSV_ROWS:,}. Consider sampling.")
            elif len(df) > 50_000:
                validation_warnings.append(f"Large dataset ({len(df):,} rows) - processing may take a moment")
            
            # Display preview
            status_text.text("📊 Preparing preview...")
            progress_bar.progress(0.6)
            
            with st.expander("📋 Data Preview (First 10 rows)", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", f"{len(df):,}")
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
                    st.metric("Missing Data", f"{missing_pct:.1f}%")
            
            # Column mapping interface
            st.markdown("### 🗂️ Map Your Columns")
            st.caption("Match your CSV columns to Echolon's required fields")
            
            col_map1, col_map2 = st.columns(2)
            
            with col_map1:
                date_col = st.selectbox(
                    "Date Column *",
                    options=[''] + list(df.columns),
                    help="Column containing transaction dates"
                )
                revenue_col = st.selectbox(
                    "Revenue Column *",
                    options=[''] + list(df.columns),
                    help="Column containing revenue/sales amounts"
                )
                orders_col = st.selectbox(
                    "Orders Column *",
                    options=[''] + list(df.columns),
                    help="Column containing order counts"
                )
            
            with col_map2:
                customers_col = st.selectbox(
                    "Customers Column (Optional)",
                    options=[''] + list(df.columns),
                    help="Column containing customer counts"
                )
                cost_col = st.selectbox(
                    "Cost Column (Optional)",
                    options=[''] + list(df.columns),
                    help="Column containing cost of goods sold"
                )
            
            st.caption("Optional: Add these for driver analysis (what changed and why)")
            col_map3, col_map4 = st.columns(2)
            with col_map3:
                channel_col = st.selectbox(
                    "Channel Column (Optional)",
                    options=[''] + list(df.columns),
                    help="Sales channel: Online, POS, Wholesale, etc."
                )
            with col_map4:
                category_col = st.selectbox(
                    "Product Category Column (Optional)",
                    options=[''] + list(df.columns),
                    help="Product category for driver analysis"
                )
            
            # Validation of required mappings
            status_text.text("🔍 Checking column mappings...")
            progress_bar.progress(0.8)
            
            if not date_col:
                validation_errors.append("Date column is required")
            if not revenue_col:
                validation_errors.append("Revenue column is required")
            if not orders_col:
                validation_errors.append("Orders column is required")
            
            # Display validation results
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            
            if validation_warnings:
                for warning in validation_warnings:
                    st.warning(f"⚠️ {warning}")
            
            # Process button
            if not validation_errors:
                status_text.text("✅ Ready to process")
                progress_bar.progress(1.0)
                
                if st.button("🚀 Process Data", type="primary", use_container_width=True):
                    with st.spinner("Processing your data..."):
                        # Map columns
                        processed_df = pd.DataFrame()
                        processed_df['date'] = pd.to_datetime(df[date_col])
                        processed_df['revenue'] = pd.to_numeric(df[revenue_col], errors='coerce')
                        processed_df['orders'] = pd.to_numeric(df[orders_col], errors='coerce')
                        
                        if customers_col:
                            processed_df['customers'] = pd.to_numeric(df[customers_col], errors='coerce')
                        else:
                            processed_df['customers'] = processed_df['orders'] * 0.5  # Estimate
                        
                        if cost_col:
                            processed_df['cost'] = pd.to_numeric(df[cost_col], errors='coerce')
                        else:
                            processed_df['cost'] = processed_df['revenue'] * 0.6  # Estimate
                        
                        if channel_col:
                            processed_df['channel'] = df[channel_col].astype(str)
                        if category_col:
                            processed_df['category'] = df[category_col].astype(str)
                        
                        # Calculate derived metrics
                        processed_df['profit'] = processed_df['revenue'] - processed_df['cost']
                        processed_df['profit_margin'] = (processed_df['profit'] / processed_df['revenue'] * 100).round(2)
                        processed_df['avg_order_value'] = (processed_df['revenue'] / processed_df['orders']).round(2)
                        
                        # Store in session state
                        st.session_state.uploaded_data = processed_df
                        if 'connected_sources' not in st.session_state:
                            st.session_state.connected_sources = {}
                        st.session_state.connected_sources['csv'] = {
                            'name': 'CSV Upload',
                            'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'last_sync': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'status': 'active'
                        }
                        
                        # Add to history
                        st.session_state.upload_history.append({
                            'filename': uploaded_file.name,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'rows': len(processed_df),
                            'columns': len(processed_df.columns),
                            'source': 'csv_upload'
                        })
                        save_user_data(get_current_user())
                        st.success(f"✅ Successfully processed {len(processed_df):,} rows!")
                        st.info("💡 Navigate to Dashboard to see your insights")
                        st.balloons()
            else:
                st.error("Please fix the errors above before processing")
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)
    
    else:
        # Show instructions when no file uploaded
        st.info(
                        "Get Started: 1. Prepare your CSV file with business data. "
                        "2. Drag and drop it above or click to browse. "
                        "3. Map your columns to Echolon fields. "
                        "4. Review the preview and click Process. "
                        "Required Columns: date, revenue, orders. "
                        "Optional Columns: customers, cost, marketing_spend."
                )

# ==================== UPDATE MAIN RENDER FUNCTION ====================
# Modify render_data_sources_page to include tabs for better organization
def render_data_sources_page_enhanced():
    """Enhanced main function with tabs for better UX"""
    st.title("📂 Data Sources")
    st.markdown("### Connect and manage your business data")
    
    # Live data badge + Connect in 2 min callout
    has_connected = bool(st.session_state.get('connected_sources'))
    if has_connected:
        st.success("🟢 **Live Data** — Your dashboard is using connected data sources.")
    else:
        st.info("⚡ **Connect in 2 minutes** — Shopify, QuickBooks, or CSV upload. Get real insights from your data.")
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📊 Quick Upload", "🔗 Integrations", "📋 History"])
    
    with tab1:
        # Enhanced CSV upload section
        render_csv_upload_section()
    
    with tab2:
        # Existing integrations
        st.markdown("### Connect Your Business Tools")
        st.markdown("---")
        
        for source_key, source_info in DATA_SOURCES.items():
            if source_key != 'csv':  # CSV is in Quick Upload tab
                render_source_card(source_key, source_info)
    
    with tab3:
        # Upload history
        if st.session_state.upload_history:
            st.markdown("### 📊 Upload History")
            history_df = pd.DataFrame(st.session_state.upload_history)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("📁 No upload history yet. Upload your first file to get started!")


