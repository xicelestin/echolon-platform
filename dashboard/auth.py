"""Authentication module for Echolon AI Platform

Provides simple username/password authentication using Streamlit secrets.
No database required - perfect for MVP with pilot customers.
Login persists across page refresh via session token in URL.

Usage:
    from auth import require_authentication
    
    # At the top of app.py, before any other content:
    if not require_authentication():
        st.stop()
"""

import os
import streamlit as st
import hashlib
import hmac


def _get_query_param(key: str):
    """Get query param - works with Streamlit 1.28+ (experimental) or 1.30+ (query_params)."""
    if hasattr(st, "query_params"):
        val = st.query_params.get(key)
        return val[0] if isinstance(val, list) else val
    return st.experimental_get_query_params().get(key, [None])[0]


def _set_query_param(key: str, value: str):
    """Set query param."""
    if hasattr(st, "query_params"):
        st.query_params[key] = value
    else:
        params = st.experimental_get_query_params()
        params = {k: (v[0] if isinstance(v, list) and v else v) for k, v in params.items()}
        params[key] = value
        st.experimental_set_query_params(**params)


def _clear_query_params():
    """Clear all query params."""
    if hasattr(st, "query_params"):
        st.query_params.clear()
    else:
        st.experimental_set_query_params()

# In production, set ECHOLON_PRODUCTION=true to disable demo credentials
IS_PRODUCTION = os.getenv("ECHOLON_PRODUCTION", "").lower() in ("true", "1", "yes")


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(username: str, password: str) -> bool:
    """Verify username and password against stored credentials."""
    
    # Demo credentials disabled in production (set ECHOLON_PRODUCTION=true)
    if not IS_PRODUCTION and username == "demo" and password == "demo123":
        st.warning("⚠️ Using demo credentials. Set ECHOLON_PRODUCTION=true to disable.")
        return True
    
    # Try to get credentials from Streamlit secrets
    try:
        users = st.secrets.get("users", {})
        
        if username in users:
            stored_password_hash = users[username]
            input_password_hash = hash_password(password)
            return hmac.compare_digest(stored_password_hash, input_password_hash)
        
        return False
        
    except Exception as e:
        # If secrets not configured, deny access
        return False

def render_landing_page():
    """Render landing page with value prop, features, and pricing."""
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;background:linear-gradient(135deg,#1e3a5f 0%,#0f172a 100%);border-radius:20px;margin-bottom:2rem;border:1px solid rgba(59,130,246,0.3);">
        <h1 style="font-size:2.5rem;color:white;margin:0 0 0.5rem 0;">🎯 Echolon AI</h1>
        <p style="font-size:1.2rem;color:#93c5fd;margin:0;">Business intelligence that tells you what to do next</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Why Echolon?")
    st.markdown("Get a 30-second briefing, actionable insights, and cash flow visibility — no analyst needed.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("**📋 Executive Briefing**")
            st.caption("Your business at a glance. Do This Week, cash flow, and top opportunities — in 30 seconds.")
    with col2:
        with st.container(border=True):
            st.markdown("**📊 Data-Driven Insights**")
            st.caption("Real patterns from your data. Channel shifts, seasonality, and margin opportunities.")
    with col3:
        with st.container(border=True):
            st.markdown("**🔗 Connect Your Data**")
            st.caption("CSV, Stripe, Shopify. Map what you have — no data team required.")
    
    st.subheader("Pricing")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#059669 0%,#047857 100%);padding:2rem;border-radius:16px;text-align:center;margin:1rem 0;border:1px solid #10b981;">
        <p style="font-size:2.5rem;font-weight:700;color:white;margin:0;">$50</p>
        <p style="color:rgba(255,255,255,0.95);font-size:1rem;margin:0 0 1rem 0;">per month</p>
        <p style="color:rgba(255,255,255,0.95);text-align:left;max-width:400px;margin:0 auto;font-size:0.95rem;">
            ✓ Executive Briefing & Dashboard<br>
            ✓ Predictions, What-If, Recommendations<br>
            ✓ Connect CSV, Stripe, Shopify<br>
            ✓ Export PDF, Excel, Weekly Digest<br>
            ✓ Industry benchmarks & alerts
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🚀 Get Started", type="primary", use_container_width=True):
        st.session_state.auth_view = "login"
        st.rerun()


def render_login_page():
    """Render professional login page"""
    
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .login-header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .login-header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        .login-header p {
            font-size: 16px;
            opacity: 0.9;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="login-header">
            <h1>🎯 Echolon AI</h1>
            <p>Business Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submit = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submit:
                if username and password:
                    if check_password(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        # Create persistent session (survives refresh)
                        from utils.session_store import create_session
                        token = create_session(username)
                        _set_query_param("session", token)
                        # Load any saved data for this account
                        from utils.user_data_storage import load_user_data
                        if load_user_data(username):
                            st.success(f"✅ Welcome back, {username}! Your data has been restored.")
                        else:
                            st.success(f"✅ Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Demo credentials hint (hidden in production)
        if not IS_PRODUCTION:
            with st.expander("💡 Demo Access"):
                st.info("""
                **Demo Credentials:**
                - Username: `demo`
                - Password: `demo123`
                
                *Set ECHOLON_PRODUCTION=true to disable in production.*
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)


def logout():
    """Logout current user and clear session data (data stays saved on disk for next login)."""
    # Remove session token so refresh won't auto-login
    token = _get_query_param("session")
    if token:
        from utils.session_store import destroy_session
        destroy_session(token)
        _clear_query_params()
    st.session_state.authenticated = False
    st.session_state.username = None
    # Clear user-specific session data so next user doesn't see it
    for key in ("uploaded_data", "connected_sources", "upload_history", "goals", "current_data"):
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def require_authentication() -> bool:
    """Main authentication function - call this at the top of app.py
    
    Returns:
        bool: True if authenticated, False if login page is shown
    """
    # Check for persistent session token (survives page refresh)
    token = _get_query_param("session")
    if token:
        from utils.session_store import validate_session
        username = validate_session(token)
        if username:
            st.session_state.authenticated = True
            st.session_state.username = username
            # Load user data on restore-from-token
            from utils.user_data_storage import load_user_data
            load_user_data(username)
            return True
        # Invalid/expired token - clear it
        _clear_query_params()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'auth_view' not in st.session_state:
        st.session_state.auth_view = "landing"
    
    # If not authenticated, show landing or login
    if not st.session_state.authenticated:
        if st.session_state.auth_view == "landing":
            render_landing_page()
        else:
            if st.button("← Back", key="auth_back"):
                st.session_state.auth_view = "landing"
                st.rerun()
            render_login_page()
        return False
    
    return True


def get_current_user() -> str:
    """Get currently logged in username"""
    return st.session_state.get('username', 'Guest')


def render_user_info():
    """Render user info in sidebar with logout button"""
    
    if st.session_state.get('authenticated', False):
        username = get_current_user()
        
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"### 👤 {username}")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()


# ====================
# PASSWORD HASH GENERATOR
# ====================
# Use this to generate password hashes for your secrets.toml

def generate_password_hash(password: str) -> str:
    """Generate a password hash for secrets.toml
    
    Usage (in Python console):
        from auth import generate_password_hash
        print(generate_password_hash("mypassword123"))
    """
    return hash_password(password)
