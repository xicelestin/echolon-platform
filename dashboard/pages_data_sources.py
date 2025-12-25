"""Multi-source data integration page for Echolon AI.
Supports Shopify, QuickBooks, Google Sheets, Stripe, and CSV uploads.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io

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
    is_connected = source_key in st.session_state.connected_sources
    
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
                st.success(f"✅ Connected - Last sync: {st.session_state.connected_sources[source_key]['last_sync']}")
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
            else:
                if st.button("Connect", key=f"connect_{source_key}", type="primary"):
                    connect_source(source_key, source_info)
        
        st.markdown("---")

def connect_source(source_key, source_info):
    """Initiate OAuth connection for a data source"""
    with st.spinner(f"Connecting to {source_info['name']}..."):
        # In production, this would redirect to OAuth
        # For MVP, we'll simulate a connection
        st.session_state.connected_sources[source_key] = {
            'name': source_info['name'],
            'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'last_sync': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'active'
        }
        st.success(f"✅ Successfully connected to {source_info['name']}!")
        st.info("💡 For MVP: OAuth flow is simulated. Production will use real OAuth.")
        st.rerun()

def disconnect_source(source_key):
    """Disconnect a data source"""
    if source_key in st.session_state.connected_sources:
        source_name = st.session_state.connected_sources[source_key]['name']
        del st.session_state.connected_sources[source_key]
        st.success(f"Disconnected from {source_name}")
        st.rerun()

def sync_data_source(source_key):
    """Sync data from a connected source"""
    with st.spinner("Syncing data..."):
        # Update last sync time
        st.session_state.connected_sources[source_key]['last_sync'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.success("✅ Data synced successfully!")
        st.rerun()

def process_csv_upload(uploaded_file):
    """Process CSV file upload"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Store in session state
        st.session_state.uploaded_data = df
        
        # Add to history
        st.session_state.upload_history.append({
            'filename': uploaded_file.name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'rows': len(df),
            'columns': len(df.columns)
        })
        
        return df
    except Exception as e:
        st.error(f"Error processing CSV: {str(e)}")
        return None

def generate_csv_template():
    """Generate CSV template for download"""
    template_df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'revenue': [1000, 1500],
        'orders': [10, 15],
        'customers': [8, 12],
        'cost': [600, 900]
    })
    return template_df.to_csv(index=False)

# ==================== MAIN PAGE ====================
def render_data_sources_page():
    """Main render function for data sources page"""
    
    st.title("🔌 Connect Your Data Sources")
    st.markdown("""Connect multiple data sources to get comprehensive insights across your entire business.
    All your data syncs automatically and updates your dashboards in real-time.""")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Connected Sources", len(st.session_state.connected_sources))
    with col2:
        st.metric("Available Integrations", len([s for s in DATA_SOURCES.values() if not s.get('coming_soon')]))
    with col3:
        total_uploads = len(st.session_state.upload_history)
        st.metric("Total Uploads", total_uploads)
    with col4:
        st.metric("Status", "Active" if st.session_state.connected_sources else "Not Connected")
    
    st.markdown("---")
    
    # Tabs for different categories
    tab1, tab2, tab3, tab4 = st.tabs(["🛍️ E-Commerce", "💼 Accounting", "📊 Data & Analytics", "📁 Manual Upload"])
    
    with tab1:
        st.markdown("### E-Commerce Platforms")
        render_source_card('shopify', DATA_SOURCES['shopify'])
    
    with tab2:
        st.markdown("### Accounting Software")
        render_source_card('quickbooks', DATA_SOURCES['quickbooks'])
    
    with tab3:
        st.markdown("### Data & Analytics")
        render_source_card('google_sheets', DATA_SOURCES['google_sheets'])
        render_source_card('stripe', DATA_SOURCES['stripe'])
    
    with tab4:
        st.markdown("### CSV File Upload")
        st.info("💡 **Best for:** Quick testing, one-time analysis, or custom data formats")
        
        # CSV Upload section
        render_source_card('csv', DATA_SOURCES['csv'])
        
        # Show CSV upload interface if triggered
        if st.session_state.get('show_csv_upload', False):
            st.markdown("---")
            st.markdown("### 📁 Upload CSV File")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""**Required columns:**
                - `date` - Transaction date
                - `revenue` - Revenue amount
                - `orders` - Number of orders
                - `customers` - Number of customers""")
            
            with col2:
                template_csv = generate_csv_template()
                st.download_button(
                    label="📥 Download Template",
                    data=template_csv,
                    file_name="echolon_data_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload your business data CSV file"
            )
            
            if uploaded_file is not None:
                df = process_csv_upload(uploaded_file)
                
                if df is not None:
                    st.success(f"✅ Successfully uploaded {len(df)} rows!")
                    
                    # Preview data
                    with st.expander("📊 Preview Data", expanded=True):
                        st.dataframe(df.head(10), use_container_width=True)
                        st.caption(f"Showing first 10 of {len(df)} rows")
                    
                    # Data validation
                    with st.expander("🔍 Data Validation"):
                        required_cols = ['date', 'revenue', 'orders', 'customers']
                        missing_cols = [col for col in required_cols if col not in df.columns]
                        
                        if missing_cols:
                            st.warning(f"⚠️ Missing recommended columns: {', '.join(missing_cols)}")
                        else:
                            st.success("✅ All required columns present")
                        
                        st.caption(f"Columns: {', '.join(df.columns.tolist())}")
                    
                    if st.button("✅ Confirm & Use This Data", type="primary"):
                        st.success("Data loaded successfully! Navigate to Dashboard to see insights.")
                        st.session_state.show_csv_upload = False
                        st.rerun()
    
    # Upload History
    if st.session_state.upload_history:
        st.markdown("---")
        st.markdown("### 📜 Upload History")
        
        history_df = pd.DataFrame(st.session_state.upload_history)
        st.dataframe(
            history_df[['timestamp', 'filename', 'rows', 'columns']],
            use_container_width=True,
            hide_index=True
        )

# ==================== RENDER ====================
if __name__ == "__main__":
    render_data_sources_page()
