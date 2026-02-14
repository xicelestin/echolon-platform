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
# On Streamlit Cloud, STREAMLIT_SERVER_BASE_URL is set - treat as production
if os.environ.get("STREAMLIT_SERVER_BASE_URL", "").startswith("https://"):
    IS_PRODUCTION = True


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
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <div style="font-family:'DM Sans',sans-serif;text-align:center;padding:4.5rem 2.5rem;background:linear-gradient(135deg,#0f172a 0%,#1e293b 40%,#0f172a 100%);border-radius:24px;margin-bottom:2.5rem;border:1px solid rgba(16,185,129,0.25);box-shadow:0 25px 50px -12px rgba(0,0,0,0.4);position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(16,185,129,0.5),transparent);opacity:0.8;"></div>
        <h1 style="font-size:3rem;font-weight:700;color:white;margin:0 0 0.75rem 0;letter-spacing:-0.03em;">Echolon AI</h1>
        <p style="font-size:1.35rem;color:#34d399;margin:0 0 1.5rem 0;font-weight:500;">Business intelligence that tells you what to do next</p>
        <p style="font-size:0.95rem;color:rgba(148,163,184,0.9);margin:0;max-width:500px;margin:0 auto;">30-second briefings. Actionable insights. No analyst needed.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style="font-family:'DM Sans',sans-serif;font-size:1.5rem;font-weight:600;color:#e2e8f0;margin-bottom:0.5rem;">Why Echolon?</h2>
    <p style="color:#94a3b8;font-size:1rem;margin-bottom:1.5rem;">Get a 30-second briefing, actionable insights, and cash flow visibility — no analyst needed.</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="font-family:'DM Sans',sans-serif;background:linear-gradient(180deg,rgba(30,41,59,0.9) 0%,rgba(15,23,42,0.95) 100%);padding:1.75rem;border-radius:16px;border:1px solid rgba(148,163,184,0.15);transition:all 0.2s;height:100%;">
            <p style="font-size:2rem;margin:0 0 0.75rem 0;">📋</p>
            <p style="font-size:1.1rem;font-weight:600;color:#f8fafc;margin:0 0 0.5rem 0;">Executive Briefing</p>
            <p style="font-size:0.9rem;color:#94a3b8;margin:0;line-height:1.5;">Your business at a glance. Do This Week, cash flow, and top opportunities — in 30 seconds.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="font-family:'DM Sans',sans-serif;background:linear-gradient(180deg,rgba(30,41,59,0.9) 0%,rgba(15,23,42,0.95) 100%);padding:1.75rem;border-radius:16px;border:1px solid rgba(16,185,129,0.2);box-shadow:0 0 0 1px rgba(16,185,129,0.1);height:100%;">
            <p style="font-size:2rem;margin:0 0 0.75rem 0;">📊</p>
            <p style="font-size:1.1rem;font-weight:600;color:#f8fafc;margin:0 0 0.5rem 0;">Data-Driven Insights</p>
            <p style="font-size:0.9rem;color:#94a3b8;margin:0;line-height:1.5;">Real patterns from your data. Channel shifts, seasonality, and margin opportunities.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="font-family:'DM Sans',sans-serif;background:linear-gradient(180deg,rgba(30,41,59,0.9) 0%,rgba(15,23,42,0.95) 100%);padding:1.75rem;border-radius:16px;border:1px solid rgba(148,163,184,0.15);height:100%;">
            <p style="font-size:2rem;margin:0 0 0.75rem 0;">🔗</p>
            <p style="font-size:1.1rem;font-weight:600;color:#f8fafc;margin:0 0 0.5rem 0;">Connect Your Data</p>
            <p style="font-size:0.9rem;color:#94a3b8;margin:0;line-height:1.5;">CSV, Stripe, Shopify. Map what you have — no data team required.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style="font-family:'DM Sans',sans-serif;font-size:1.5rem;font-weight:600;color:#e2e8f0;margin:2.5rem 0 0.5rem 0;">Pricing</h2>
    <p style="color:#94a3b8;font-size:0.95rem;margin-bottom:1.5rem;">14-day free trial on any paid plan. No credit card required.</p>
    """, unsafe_allow_html=True)
    
    col_free, col_starter, col_growth = st.columns(3)
    with col_free:
        st.markdown("""
        <div style="font-family:'DM Sans',sans-serif;background:linear-gradient(180deg,rgba(30,41,59,0.8) 0%,rgba(15,23,42,0.9) 100%);padding:1.75rem;border-radius:16px;border:1px solid rgba(148,163,184,0.15);height:100%;">
            <p style="font-size:1.1rem;font-weight:600;color:#94a3b8;margin:0;">Free</p>
            <p style="font-size:2.25rem;font-weight:700;color:#10b981;margin:0.5rem 0;">$0</p>
            <p style="color:#64748b;font-size:0.85rem;margin:0 0 1.25rem 0;">Forever free</p>
            <p style="color:#cbd5e1;font-size:0.9rem;margin:0;line-height:1.6;">
                ✓ Executive Briefing<br>✓ 1 CSV upload, 30 days<br>✓ Data Sources
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Free", key="plan_free", use_container_width=True):
            st.session_state.auth_view = "login"
            st.session_state.signup_tier = "free"
            st.rerun()
    with col_starter:
        st.markdown("""
        <div style="font-family:'DM Sans',sans-serif;background:linear-gradient(135deg,#059669 0%,#047857 100%);padding:1.75rem;border-radius:16px;border:2px solid rgba(52,211,153,0.5);height:100%;position:relative;box-shadow:0 10px 40px -10px rgba(5,150,105,0.4);">
            <span style="position:absolute;top:-10px;right:16px;background:linear-gradient(135deg,#f59e0b,#d97706);color:white;font-size:10px;font-weight:600;padding:4px 10px;border-radius:6px;letter-spacing:0.05em;">POPULAR</span>
            <p style="font-size:1.1rem;font-weight:600;color:rgba(255,255,255,0.9);margin:0;">Starter</p>
            <p style="font-size:2.25rem;font-weight:700;color:white;margin:0.5rem 0;">$49</p>
            <p style="color:rgba(255,255,255,0.85);font-size:0.85rem;margin:0 0 1.25rem 0;">/mo · $39/mo annual</p>
            <p style="color:rgba(255,255,255,0.95);font-size:0.9rem;margin:0;line-height:1.6;">
                ✓ Briefing & Dashboard<br>✓ Analytics, Insights, Goals<br>✓ 1 source, 90 days
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Free Trial", key="plan_starter", type="primary", use_container_width=True):
            st.session_state.auth_view = "login"
            st.session_state.signup_tier = "starter"
            st.rerun()
    with col_growth:
        st.markdown("""
        <div style="font-family:'DM Sans',sans-serif;background:linear-gradient(180deg,rgba(30,41,59,0.8) 0%,rgba(15,23,42,0.9) 100%);padding:1.75rem;border-radius:16px;border:1px solid rgba(16,185,129,0.25);height:100%;">
            <p style="font-size:1.1rem;font-weight:600;color:#94a3b8;margin:0;">Growth</p>
            <p style="font-size:2.25rem;font-weight:700;color:#10b981;margin:0.5rem 0;">$99</p>
            <p style="color:#64748b;font-size:0.85rem;margin:0 0 1.25rem 0;">/mo · $79/mo annual</p>
            <p style="color:#cbd5e1;font-size:0.9rem;margin:0;line-height:1.6;">
                ✓ Everything in Starter<br>✓ Predictions, What-If, Recs<br>✓ Unlimited sources, 12 mo
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Free Trial", key="plan_growth", use_container_width=True):
            st.session_state.auth_view = "login"
            st.session_state.signup_tier = "growth"
            st.rerun()
    
    st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)
    if st.button("🚀 Get Started", type="primary", use_container_width=True):
        st.session_state.auth_view = "login"
        st.rerun()


def render_login_page():
    """Render professional login page"""
    
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        .login-container {
            font-family: 'DM Sans', sans-serif;
            max-width: 420px;
            margin: 80px auto;
            padding: 2.5rem;
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
            border-radius: 20px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.4);
        }
        .login-header {
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        .login-header p {
            font-size: 0.95rem;
            color: #94a3b8;
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
            st.caption("Forgot password? Email support@echolon.ai for a reset link.")
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
    # Handle Stripe checkout success (session_id in URL after payment)
    stripe_session = _get_query_param("session_id")
    if stripe_session and stripe_session.startswith("cs_"):
        from utils.subscription import get_subscription_from_session
        sub_info = get_subscription_from_session(stripe_session)
        if sub_info and sub_info.get("status") == "active":
            # User must be logged in to attach subscription - they'll have session
            if st.session_state.get("authenticated"):
                st.session_state.stripe_subscription_status = "active"
                st.session_state.subscription_tier = sub_info.get("tier", "growth")
            _clear_query_params()
            if st.session_state.get("authenticated"):
                st.success("✅ Payment successful! Your plan is now active.")
                st.rerun()
    
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
