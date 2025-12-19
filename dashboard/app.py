import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Echolon AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 Echolon AI Dashboard")
st.markdown("### AI-Powered Business Intelligence")

st.success("✅ Dashboard is now online and working!")

# Sidebar
with st.sidebar:
    st.header("📊 Echolon AI")
    st.markdown("---")
    st.info("Dashboard successfully deployed!")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Revenue", "$124.5K", "+12.5%")

with col2:
    st.metric("Customers", "1,234", "+8.2%")

with col3:
    st.metric("Growth Rate", "15.3%", "+2.1%")

st.markdown("---")

# Sample chart
st.subheader("📈 Revenue Trend")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Revenue', 'Costs', 'Profit']
)
st.line_chart(chart_data)

st.markdown("---")
st.caption("© 2025 Echolon AI - Business Intelligence Platform")
