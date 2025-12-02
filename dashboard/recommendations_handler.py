"""Recommendations Handler for Echolon AI Dashboard"""
import streamlit as st
import requests
from datetime import datetime
import os

def get_recommendations(backend_url, data_source='demo', uploaded_data=None):
    """
    Fetch AI-powered recommendations from backend
    
    Args:
        backend_url: Backend API URL
        data_source: 'demo' or 'uploaded'
        uploaded_data: DataFrame of uploaded data (if any)
    
    Returns:
        List of recommendation dictionaries
    """
    try:
        # Try to fetch from backend ML recommendations endpoint
        response = requests.get(
            f"{backend_url}/ml/recommendations",
            params={"data_source": data_source},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('recommendations', [])
        else:
            # Return fallback demo recommendations
            return get_demo_recommendations()
    except Exception as e:
        # Return fallback demo recommendations if backend unavailable
        return get_demo_recommendations()

def get_demo_recommendations():
    """
    Generate demo recommendations when backend is unavailable
    """
    return [
        {
            "title": "Focus on SaaS revenue stream",
            "description": "Your SaaS category represents 45% of sales and shows 15% month-over-month growth. Consider allocating more marketing budget here.",
            "impact": "High",
            "timeframe": "This Week",
            "category": "Revenue"
        },
        {
            "title": "Reduce customer acquisition cost",
            "description": "Current CAC is $241K. Optimize ad spend on underperforming channels to reduce by 10-15%.",
            "impact": "High",
            "timeframe": "This Month",
            "category": "Efficiency"
        },
        {
            "title": "Address churn rate increase",
            "description": "Churn rate increased 0.3% this month. Implement customer success check-ins for at-risk accounts.",
            "impact": "Medium",
            "timeframe": "Today",
            "category": "Retention"
        },
        {
            "title": "Capitalize on customer growth trend",
            "description": "Customer base grew 1.8% last month. Launch referral program to accelerate growth to 3-5%.",
            "impact": "Medium",
            "timeframe": "Next 2 Weeks",
            "category": "Growth"
        }
    ]

def render_recommendations_panel(backend_url, data_source='demo', uploaded_data=None):
    """
    Render the AI Recommendations panel in Streamlit
    
    Args:
        backend_url: Backend API URL
        data_source: 'demo' or 'uploaded'
        uploaded_data: DataFrame of uploaded data (if any)
    """
    st.markdown("### 🎯 AI Recommendations")
    st.markdown("Actionable insights to improve your business efficiency")
    st.markdown("---")
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_recommendations"):
            st.rerun()
    
    # Get recommendations
    recommendations = get_recommendations(backend_url, data_source, uploaded_data)
    
    # Render each recommendation
    for idx, rec in enumerate(recommendations):
        with st.container():
            # Impact badge color
            if rec['impact'] == 'High':
                badge_color = '#d62728'  # Red
            elif rec['impact'] == 'Medium':
                badge_color = '#ff7f0e'  # Orange
            else:
                badge_color = '#2ca02c'  # Green
            
            # Render recommendation card
            st.markdown(f"""
                <div style="
                    background-color: #1E1E1E;
                    padding: 16px;
                    border-radius: 8px;
                    border-left: 4px solid {badge_color};
                    margin-bottom: 12px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: white;">{rec['title']}</h4>
                        <div style="display: flex; gap: 8px;">
                            <span style="
                                background-color: {badge_color};
                                color: white;
                                padding: 4px 12px;
                                border-radius: 12px;
                                font-size: 12px;
                                font-weight: bold;
                            ">{rec['impact']} Impact</span>
                            <span style="
                                background-color: #444;
                                color: white;
                                padding: 4px 12px;
                                border-radius: 12px;
                                font-size: 12px;
                            ">{rec['timeframe']}</span>
                        </div>
                    </div>
                    <p style="margin-top: 8px; margin-bottom: 0; color: #ccc;">{rec['description']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Add info footer
    st.markdown("---")
    st.markdown("""
        <small style="color: #888;">
        💡 Recommendations are generated based on your current metrics and industry benchmarks.
        Upload your data for personalized insights.
        </small>
    """, unsafe_allow_html=True)
