"""Admin Settings & Setup Panel for Echolon AI Platform.

Provides:
- Data source connection management (Stripe, Shopify, APIs)
- User management and role assignments
- API key generation and management
- Audit logs for compliance
- Organization settings
"""

import streamlit as st
import requests
from datetime import datetime
import json
from error_ui import (
    display_error, display_warning, display_success,
    safe_api_call, retry_button, error_recovery_form,
    log_error, error_history_widget
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Echolon AI - Admin Settings",
    page_icon="⚙️",
    layout="wide",
)

# ============================================================================
# SESSION STATE & AUTHENTICATION
# ============================================================================

if not st.session_state.get("is_authenticated", False):
    st.error("⛔ Please log in first")
    st.stop()

# Check admin role
if st.session_state.get("role") != "admin":
    st.error("🚫 Admin access required. You are a: " + st.session_state.get("role", "unknown"))
    st.stop()

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8000/api"
DATA_SOURCE_TYPES = ["stripe", "shopify", "google_sheets", "sql_database", "api", "csv_upload"]

def get_headers():
    """Get auth headers for API requests."""
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"}

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
    <div style='text-align: center;'>
        <h1>⚙️ Admin Settings</h1>
        <p style='color: #999;'>Manage data sources, users, and API keys</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# User info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👤 Logged In As", st.session_state.get("email", "Unknown"))
with col2:
    st.metric("🔐 Role", st.session_state.get("role", "Unknown").upper())
with col3:
    st.metric("✅ Status", "Active")

st.markdown("---")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Data Sources",
    "👥 User Management",
    "🔑 API Keys",
    "📋 Audit Logs",
])

# ============================================================================
# TAB 1: DATA SOURCES
# ============================================================================

with tab1:
    st.subheader("📊 Data Source Connections")
    st.write("Connect your business data sources for analysis.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ➕ Add New Data Source")
        with st.form("add_datasource_form"):
            source_name = st.text_input(
                "Data Source Name",
                placeholder="e.g., Main Stripe Account",
            )
            source_type = st.selectbox(
                "Data Source Type",
                options=DATA_SOURCE_TYPES,
                help="Type of data source to connect",
            )
            
            st.markdown("**Credentials**")
            if source_type == "stripe":
                api_key = st.text_input("Stripe API Key", type="password")
                credentials_json = {"api_key": api_key}
            elif source_type == "shopify":
                shop_url = st.text_input("Shopify Store URL", placeholder="mystore.myshopify.com")
                access_token = st.text_input("Access Token", type="password")
                credentials_json = {"shop_url": shop_url, "access_token": access_token}
            elif source_type == "api":
                endpoint = st.text_input("API Endpoint", placeholder="https://api.example.com")
                auth_type = st.selectbox("Auth Type", ["Bearer", "API Key", "Basic"])
                credentials_json = {"endpoint": endpoint, "auth_type": auth_type}
            else:
                st.info("ℹ️ Configuration coming soon for this source type")
                credentials_json = {}
            
            submitted = st.form_submit_button("✅ Connect Data Source", use_container_width=True)
                        if submitted:
                try:
                    # API call would go here
                    display_success(f"Data source '{source_name}' connected successfully!")
                except Exception as e:
                    display_error(
                        f"Failed to connect data source",
                        error_code="DATASOURCE_CONNECT_ERROR",
                        error_detail=str(e),
                        request_id="admin-datasource-123"
                    )
                    log_error(
                        error_code="DATASOURCE_CONNECT_ERROR",
                        message="Failed to connect data source",
                        detail=str(e)
                    )
            
            if submitted:
                if not source_name or not credentials_json:
                    st.error("❌ Please fill in all required fields")
                else:
                    st.success(f"✅ Data source '{source_name}' connected!")
                    st.info("💡 Your data will sync automatically every 24 hours")
    
    with col2:
        st.markdown("### 📦 Connected Sources")
        st.markdown("""
            #### Stripe - Main Account
            - **Status**: ✅ Connected
            - **Last Sync**: 2 hours ago
            - **Records**: 12,435 transactions
            - [🔄 Sync Now] [⚙️ Edit] [🗑️ Remove]
            
            ---
            
            #### Shopify - Online Store
            - **Status**: ✅ Connected
            - **Last Sync**: 45 minutes ago
            - **Records**: 5,234 orders
            - [🔄 Sync Now] [⚙️ Edit] [🗑️ Remove]
            
            ---
            
            #### Google Sheets - Inventory
            - **Status**: ⚠️ Pending
            - **Last Sync**: Never
            - **Records**: 0
            - [🔄 Sync Now] [⚙️ Edit] [🗑️ Remove]
        """)

# ============================================================================
# TAB 2: USER MANAGEMENT
# ============================================================================

with tab2:
    st.subheader("👥 User Management")
    st.write("Manage team members and assign roles.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ➕ Invite New User")
        with st.form("invite_user_form"):
            email = st.text_input("Email Address", placeholder="user@company.com")
            full_name = st.text_input("Full Name", placeholder="John Doe")
            role = st.selectbox(
                "Role",
                ["Analyst", "Viewer"],
                help="Admins can only be set manually for security",
            )
            
            submitted = st.form_submit_button("📧 Send Invite", use_container_width=True)
            if submitted and email:
                st.success(f"✅ Invitation sent to {email}")
    
    with col2:
        st.markdown("### 👥 Team Members")
        st.markdown("""
            | Email | Name | Role | Status | Actions |
            |-------|------|------|--------|----------|
            | you@company.com | You | Admin | Active | (Owner) |
            | analyst@company.com | Jane Smith | Analyst | Active | [Edit] [Remove] |
            | viewer@company.com | Bob Johnson | Viewer | Active | [Edit] [Remove] |
            | pending@company.com | Alice Brown | Analyst | Pending | [Resend] [Cancel] |
        """)

# ============================================================================
# TAB 3: API KEYS
# ============================================================================

with tab3:
    st.subheader("🔑 API Key Management")
    st.write("Create and manage API keys for third-party integrations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ➕ Generate New API Key")
        with st.form("generate_api_key_form"):
            key_name = st.text_input(
                "Key Name",
                placeholder="Production API Key",
                help="Descriptive name for this key",
            )
            permissions = st.multiselect(
                "Permissions",
                ["read:dashboard", "read:data", "write:data", "read:analytics", "admin"],
                default=["read:dashboard", "read:data"],
                help="Select which endpoints this key can access",
            )
            
            submitted = st.form_submit_button("✅ Generate Key", use_container_width=True)
            if submitted and key_name:
                # Simulated key generation
                new_key = f"ek_1a2b3c4d5e6f7g8h9i0j_live"
                st.success("✅ API Key Generated!")
                st.code(new_key, language="text")
                st.warning("⚠️ Save this key somewhere safe. You won't see it again!")
    
    with col2:
        st.markdown("### 🔑 Active API Keys")
        st.markdown("""
            #### Production API Key
            - **Permissions**: read:dashboard, read:data, write:data
            - **Created**: Dec 1, 2025
            - **Last Used**: 2 hours ago
            - [🔄 Rotate] [🗑️ Revoke]
            
            ---
            
            #### Development API Key
            - **Permissions**: read:dashboard, read:data
            - **Created**: Nov 15, 2025
            - **Last Used**: Never
            - [🔄 Rotate] [🗑️ Revoke]
        """)

# ============================================================================
# TAB 4: AUDIT LOGS
# ============================================================================

with tab4:
    st.subheader("📋 Audit Logs")
    st.write("Track all admin actions for compliance and security.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("**Filter by Action Type**")
    with col2:
        action_filter = st.selectbox(
            "Action Type",
            ["All", "user_created", "user_deleted", "role_updated", "datasource_added", "api_key_generated"],
            label_visibility="collapsed",
        )
    
    st.markdown("""|
        Timestamp | User | Action | Details | IP Address |
        |-----------|------|--------|---------|-------------|
        | 2025-12-23 03:15 | you@company.com | datasource_added | Stripe connected | 192.168.1.1 |
        | 2025-12-22 14:32 | you@company.com | api_key_generated | Production key | 192.168.1.1 |
        | 2025-12-22 10:01 | you@company.com | user_created | Jane Smith (Analyst) | 192.168.1.1 |
        | 2025-12-21 16:45 | you@company.com | role_updated | Bob Johnson: Viewer → Analyst | 192.168.1.1 |
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px;'>
        💡 Need help? <a href='#'>View Documentation</a> | 
        🐛 Found a bug? <a href='#'>Report Issue</a> | 
        📧 Questions? <a href='mailto:support@echolon.ai'>Email Support</a>
    </div>
    """,
    unsafe_allow_html=True,
)
