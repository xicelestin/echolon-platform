"""Main Streamlit app for Echolon AI Dashboard.

Orchestrates the multi-page dashboard with authentication,
error handling, and data visualization.
"""

import streamlit as st
from streamlit_option_menu import option_menu
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Echolon AI - Business Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 0rem;
    }
    .metric-card {
        border-radius: 10px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def check_authentication():
    """Check if user is authenticated."""
    if "token" not in st.session_state or not st.session_state.token:
        st.switch_page("pages/login.py")
        return False
    return True

def render_header():
    """Render the header section."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🚀 Echolon AI")
        st.caption("Business Intelligence Platform")
    
    with col3:
        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.switch_page("pages/login.py")

def render_navigation():
    """Render the main navigation menu."""
    with st.sidebar:
        st.markdown("---")
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Dashboard",
                "Analytics",
                "Predictions",
                "Recommendations",
                "What-If Analysis",
                "Inventory",
                "Upload Data",
                "Customer Insights",
                "Inventory & Demand",
                "Anomalies & Alerts",
            ],
            icons=[
                "house-fill",
                "bar-chart",
                "crystal-ball",
                "lightbulb",
                "question-circle",
                "boxes",
                "cloud-upload",
                "people",
                "boxes-3",
                "exclamation-triangle",
            ],
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        st.markdown("**Settings**")
        if st.button("⚙️ Admin Settings", key="admin_btn", use_container_width=True):
            st.switch_page("pages/admin.py")
        
        st.markdown("---")
        user_info = st.session_state.get("user", {})
        st.caption(f"Logged in as: {user_info.get('email', 'Unknown')}")
        
        return selected

def render_main_content(page_name):
    """Render the main content based on selected page."""
    
    if page_name == "Dashboard":
        render_dashboard()
    elif page_name == "Analytics":
        render_analytics()
    elif page_name == "Predictions":
        render_predictions()
    elif page_name == "Recommendations":
        render_recommendations()
    elif page_name == "What-If Analysis":
        render_whatif_analysis()
    elif page_name == "Inventory":
        render_inventory()
    elif page_name == "Upload Data":
        render_upload_data()
    elif page_name == "Customer Insights":
        render_customer_insights()
    elif page_name == "Inventory & Demand":
        render_inventory_demand()
    elif page_name == "Anomalies & Alerts":
        render_anomalies_alerts()

def render_dashboard():
    """Render the main dashboard."""
    st.header("📊 AI-Powered Predictions")
    st.subheader("Forecast future performance using AI")
    
    # Forecast control
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Forecast Days Ahead**")
    with col2:
        forecast_days = st.slider("Days", min_value=1, max_value=90, value=30, key="forecast_slider")
    
    # Sample metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Predicted Revenue", "$1,762,031", "+2.3%")
    
    with col2:
        st.metric("Avg Daily Revenue", "$58,734.37", "+1.8%")
    
    with col3:
        st.metric("Expected Change", "+2.3%", "↑ Positive Trend")
    
    # Revenue Forecasting
    st.header("📈 Revenue Forecasting")
    st.subheader("Revenue Forecast - Next 30 Days")
    
    # Placeholder for chart
    st.info("📊 Revenue forecast chart will be displayed here", icon="ℹ️")
    
    # Historical vs Forecast comparison
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Predicted Total Revenue", "$1,762,031")
    with col2:
        st.metric("Predicted Avg Daily Revenue", "$58,734.37")
    with col3:
        st.metric("Expected Change", "+2.3%")

def render_analytics():
    """Render analytics page placeholder."""
    st.header("📊 Analytics")
    st.info("Analytics page coming soon", icon="ℹ️")

def render_predictions():
    """Render predictions page placeholder."""
    st.header("🔮 Predictions")
    st.info("Predictions page coming soon", icon="ℹ️")

def render_recommendations():
    """Render recommendations page placeholder."""
    st.header("💡 Recommendations")
    st.info("Recommendations page coming soon", icon="ℹ️")

def render_whatif_analysis():
    """Render what-if analysis page placeholder."""
    st.header("❓ What-If Analysis")
    st.info("What-If Analysis page coming soon", icon="ℹ️")

def render_inventory():
    """Render inventory page placeholder."""
    st.header("📦 Inventory")
    st.info("Inventory page coming soon", icon="ℹ️")

def render_upload_data():
    """Render upload data page placeholder."""
    st.header("📤 Upload Data")
    st.info("Upload Data page coming soon", icon="ℹ️")

def render_customer_insights():
    """Render customer insights page placeholder."""
    st.header("👥 Customer Insights")
    st.info("Customer Insights page coming soon", icon="ℹ️")

def render_inventory_demand():
    """Render inventory and demand page placeholder."""
    st.header("📊 Inventory & Demand")
    st.info("Inventory & Demand page coming soon", icon="ℹ️")

def render_anomalies_alerts():
    """Render anomalies and alerts page placeholder."""
    st.header("⚠️ Anomalies & Alerts")
    st.info("Anomalies & Alerts page coming soon", icon="ℹ️")

def main():
    """Main application entry point."""
    # Check authentication
    if not check_authentication():
        return
    
    # Initialize session state
    if "user" not in st.session_state:
        st.session_state.user = {"email": "demo@example.com"}
    
    try:
        # Render header
        render_header()
        
        # Render navigation and get selected page
        selected_page = render_navigation()
        
        # Render main content
        render_main_content(selected_page)
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}", exc_info=True)
        st.error("❌ An error occurred while rendering the dashboard. Please refresh the page.")
        st.exception(e)

if __name__ == "__main__":
    main()
