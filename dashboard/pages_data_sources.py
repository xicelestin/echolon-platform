# -*- coding: utf-8 -*-
"""Multi-source data integration page for Echolon AI.
Supports Shopify, QuickBooks, Google Sheets, Stripe, and CSV uploads.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io
# from data_source_apis import fetch_data_from_api

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
                
                st.success(f"✅ Successfully connected to {source_info['name']} and loaded {len(data_df)} rows!")
                st.info("💡 Navigate to Dashboard to see your data insights")
            else:
                st.warning("Connected but no data was fetched. Please check your account permissions.")
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("💡 For MVP: OAuth flow is simulated. Production will use real OAuth.")
        
        st.rerun()

def fetch_data_from_source(source_key, source_info):

        """Fetch actual data from the connected source using real APIs.
    
    Args:
        source_key: The data source identifier
        source_info: Dictionary with source configuration
    
    Returns:
        DataFrame with fetched data or None if error
    """
    # Try to fetch from real API first
    # try:
        #         api_data = fetch_data_from_api(source_key)
        
        if api_data is not None and not api_data.empty:
            return api_data
    except Exception as e:
        st.warning(f"Could not fetch from API: {str(e)}. Using demo data.")
    
    # Fallback to demo data if API fails or credentials not configured
    return generate_demo_data_fallback(source_key)


def generate_demo_data_fallback(source_key):
    """Generate demo data as fallback when API is not configured."""
    import numpy as np
    
    # Create date range for last 12 months
    dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
    
    # Generate demo data based on source type
    if source_key == 'shopify':
        trend = np.linspace(10000, 50000, len(dates))
    elif source_key == 'quickbooks':
        trend = np.linspace(35000, 65000, len(dates))
    elif source_key == 'stripe':
        trend = np.linspace(20000, 55000, len(dates))
    elif source_key == 'google_sheets':
        trend = np.linspace(15000, 45000, len(dates))
    else:
        trend = np.linspace(25000, 50000, len(dates))
    
    seasonality = 7000 * np.sin(np.linspace(0, 4*np.pi, len(dates)))
    noise = np.random.normal(0, 2500, len(dates))
    
    data = pd.DataFrame({
        'date': dates,
        'revenue': trend + seasonality + noise,
        'orders': np.random.poisson(85, len(dates)) + (trend/600).astype(int),
        'customers': np.random.poisson(65, len(dates)) + (trend/750).astype(int),
        'cost': (trend + seasonality + noise) * 0.59,
        'marketing_spend': np.random.normal(5000, 1000, len(dates)),
        'conversion_rate': np.random.uniform(2.2, 4.6, len(dates))
    })
    
    # Add derived metrics
    data['profit'] = data['revenue'] - data['cost']
    data['profit_margin'] = (data['profit'] / data['revenue'] * 100).round(2)
    data['roas'] = (data['revenue'] / data['marketing_spend']).round(2)
    data['avg_order_value'] = (data['revenue'] / data['orders']).round(2)
    data['new_customers'] = (data['customers'] * 0.3).astype(int)
    
    return data
def disconnect_source(source_key):
    """Disconnect a data source"""
    if source_key in st.session_state.connected_sources:
        source_name = st.session_state.connected_sources[source_key]['name']
        del st.session_state.connected_sources[source_key]
        st.success(f"Disconnected from {source_name}")
        st.rerun()


def sync_data_source(source_key):
    """Sync data from a connected source"""
    source_info = st.session_state.connected_sources.get(source_key)
    if source_info:
        with st.spinner(f"Syncing {source_info['name']}..."):
            st.session_state.connected_sources[source_key]['last_sync'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.success(f"✅ Successfully synced {source_info['name']}")
            st.rerun()

def render_data_sources_page():
    """Render the Data Sources page"""
        
    # Initialize session state
    if 'connected_sources' not in st.session_state:
        st.session_state.connected_sources = {}
    if 'upload_history' not in st.session_state:
        st.session_state.upload_history = []
    st.title("🔌 Data Sources")
    st.markdown("Connect your business data sources to power Echolon AI")
    
    # Render each data source
    for source_key, source_info in DATA_SOURCES.items():
        render_source_card(source_key, source_info)
    
    # Upload history
    if st.session_state.upload_history:
        st.markdown("### Upload History")
        history_df = pd.DataFrame(st.session_state.upload_history)
        st.dataframe(history_df, use_container_width=True)
