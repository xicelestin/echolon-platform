"""Authentication module for Echolon AI Platform

Provides simple username/password authentication using Streamlit secrets.
No database required - perfect for MVP with pilot customers.

Usage:
    from auth import require_authentication
    
    # At the top of app.py, before any other content:
    if not require_authentication():
        st.stop()
"""

import streamlit as st
import hashlib
import hmac


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(username: str, password: str) -> bool:
    """Verify username and password against stored credentials."""
    
    # Demo credentials (for development/pilot customers)
    # Remove this section in production
    if username == "demo" and password == "demo123":
        st.warning("⚠️ Using demo credentials. Configure secrets for production.")
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
                        st.success(f"✅ Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Demo credentials hint (remove in production)
        with st.expander("💡 Demo Access"):
            st.info("""
            **Demo Credentials:**
            - Username: `demo`
            - Password: `demo123`
            
            *For pilot customers: Contact your account manager for credentials.*
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)


def logout():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()


def require_authentication() -> bool:
    """Main authentication function - call this at the top of app.py
    
    Returns:
        bool: True if authenticated, False if login page is shown
    """
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # If not authenticated, show login page
    if not st.session_state.authenticated:
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
