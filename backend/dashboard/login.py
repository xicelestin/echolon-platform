"""Streamlit login and authentication page for Echolon AI Platform.

Provides:
- User login interface
- User registration interface
- Session management
- JWT token storage
- Protected page routing
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import re

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8000/api/auth"  # Change to deployed API URL

# Session state keys
SESSION_KEYS = {
    "user_id": "user_id",
    "email": "email",
    "role": "role",
    "access_token": "access_token",
    "refresh_token": "refresh_token",
    "token_expires_at": "token_expires_at",
    "is_authenticated": "is_authenticated",
}

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Echolon AI - Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide sidebar on login page
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, "Password is strong"

def store_tokens(access_token: str, refresh_token: str, expires_in: int, user_data: dict):
    """Store authentication tokens and user data in session state."""
    st.session_state[SESSION_KEYS["access_token"]] = access_token
    st.session_state[SESSION_KEYS["refresh_token"]] = refresh_token
    st.session_state[SESSION_KEYS["token_expires_at"]] = datetime.utcnow() + timedelta(seconds=expires_in)
    st.session_state[SESSION_KEYS["user_id"]] = user_data.get("user_id")
    st.session_state[SESSION_KEYS["email"]] = user_data.get("email")
    st.session_state[SESSION_KEYS["role"]] = user_data.get("role")
    st.session_state[SESSION_KEYS["is_authenticated"]] = True

def is_user_authenticated() -> bool:
    """Check if user is currently authenticated."""
    if not st.session_state.get(SESSION_KEYS["is_authenticated"], False):
        return False
    
    # Check if token has expired
    expires_at = st.session_state.get(SESSION_KEYS["token_expires_at"])
    if expires_at and datetime.utcnow() > expires_at:
        st.session_state[SESSION_KEYS["is_authenticated"]] = False
        return False
    
    return True

def get_auth_header() -> dict:
    """Get Authorization header for API requests."""
    token = st.session_state.get(SESSION_KEYS["access_token"])
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# ============================================================================
# LOGIN FORM
# ============================================================================

def login_form():
    """Display and handle login form."""
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>🔐 Echolon AI</h1>
            <p style='color: #999; font-size: 16px;'>Business Intelligence Platform</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("---")
    
    with st.form("login_form"):
        st.subheader("Login")
        
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            help="Enter your registered email address",
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            help="Enter your secure password (min 8 characters)",
        )
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("❌ Please enter both email and password")
                return
            
            if not validate_email(email):
                st.error("❌ Please enter a valid email address")
                return
            
            # Call login API
            try:
                response = requests.post(
                    f"{API_URL}/login",
                    json={"email": email, "password": password},
                    timeout=10,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Store tokens and user info
                    store_tokens(
                        access_token=data["access_token"],
                        refresh_token=data["refresh_token"],
                        expires_in=data["expires_in"],
                        user_data={"email": email, "user_id": email},  # Get from API response in production
                    )
                    st.success("✅ Login successful!")
                    st.balloons()
                    # Redirect to dashboard
                    st.switch_page("pages/dashboard.py")
                else:
                    error_msg = response.json().get("detail", "Login failed")
                    st.error(f"❌ {error_msg}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Please check your connection.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Switch to signup
    st.markdown(
        "<p style='text-align: center; color: #999;'>Don't have an account?</p>",
        unsafe_allow_html=True,
    )
    if st.button("Create account", use_container_width=True, key="switch_to_signup"):
        st.session_state["show_signup"] = True
        st.rerun()

# ============================================================================
# SIGNUP FORM
# ============================================================================

def signup_form():
    """Display and handle signup form."""
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>🔐 Echolon AI</h1>
            <p style='color: #999; font-size: 16px;'>Business Intelligence Platform</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("---")
    
    with st.form("signup_form"):
        st.subheader("Create Account")
        
        full_name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            help="Enter your full name",
        )
        
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            help="Enter your email address",
        )
        
        company_name = st.text_input(
            "Company Name (Optional)",
            placeholder="Acme Corp",
            help="Enter your company name",
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            help="Create a secure password",
        )
        
        password_confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="••••••••",
            help="Confirm your password",
        )
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            # Validation
            if not all([full_name, email, password, password_confirm]):
                st.error("❌ Please fill in all required fields")
                return
            
            if not validate_email(email):
                st.error("❌ Please enter a valid email address")
                return
            
            if password != password_confirm:
                st.error("❌ Passwords do not match")
                return
            
            is_valid, msg = validate_password(password)
            if not is_valid:
                st.error(f"❌ Password validation failed: {msg}")
                return
            
            # Call signup API
            try:
                response = requests.post(
                    f"{API_URL}/signup",
                    json={
                        "email": email,
                        "full_name": full_name,
                        "password": password,
                        "company_name": company_name,
                    },
                    timeout=10,
                )
                
                if response.status_code == 200:
                    st.success("✅ Account created successfully! Please log in.")
                    st.session_state["show_signup"] = False
                    st.rerun()
                else:
                    error_msg = response.json().get("detail", "Signup failed")
                    st.error(f"❌ {error_msg}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Please check your connection.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Switch to login
    st.markdown(
        "<p style='text-align: center; color: #999;'>Already have an account?</p>",
        unsafe_allow_html=True,
    )
    if st.button("Login here", use_container_width=True, key="switch_to_login"):
        st.session_state["show_signup"] = False
        st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main app logic."""
    # Check if user is already authenticated
    if is_user_authenticated():
        st.switch_page("pages/dashboard.py")
        return
    
    # Show signup or login form
    if st.session_state.get("show_signup", False):
        signup_form()
    else:
        login_form()

if __name__ == "__main__":
    main()
