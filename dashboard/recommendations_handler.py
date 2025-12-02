"""AI Recommendations Handler for Echolon AI Dashboard

Provides AI-powered recommendations for business efficiency improvements.
Includes backend integration with fallback demo recommendations.
"""
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
    Render the AI Recommendations panel in Streamlit with enhanced styling
    
    Args:
        backend_url: Backend API URL
        data_source: 'demo' or 'uploaded'
        uploaded_data: DataFrame of uploaded data (if any)
    """
    # Custom CSS for enhanced panel styling
    st.markdown("""
    <style>
    .rec-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .rec-header-icon {
        font-size: 20px;
    }
    .rec-header-title {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        margin: 0;
    }
    .rec-subtitle {
        font-size: 13px;
        color: #AAAAAA;
        margin: 0;
    }
    .rec-card {
        background: linear-gradient(135deg, #1F1F1F 0%, #2A2A2A 100%);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #6366F1;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .rec-card:hover {
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        transform: translateX(4px);
    }
    .rec-card-high {
        border-left-color: #EF4444;
    }
    .rec-card-medium {
        border-left-color: #F59E0B;
    }
    .rec-card-low {
        border-left-color: #10B981;
    }
    .rec-title {
        font-size: 14px;
        font-weight: 600;
        color: #FFFFFF;
        margin: 0 0 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .rec-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .rec-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 600;
        white-space: nowrap;
    }
    .rec-badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .rec-badge-medium {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .rec-badge-low {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .rec-badge-timeframe {
        background-color: #374151;
        color: #E5E7EB;
    }
    .rec-description {
        font-size: 13px;
        line-height: 1.5;
        color: #D1D5DB;
        margin: 8px 0 0 0;
    }
    .rec-footer {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #404040;
        font-size: 11px;
        color: #6B7280;
    }
    .rec-category {
        display: inline-block;
        background-color: #6366F1;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="rec-header"><span class="rec-header-icon">✨</span><h3 class="rec-header-title">AI Recommendations</h3></div>', unsafe_allow_html=True)
    st.markdown('<p class="rec-subtitle">Actionable insights to boost your business efficiency</p>', unsafe_allow_html=True)
    
    # Refresh button with better styling
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_recommendations", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Get recommendations
    recommendations = get_recommendations(backend_url, data_source, uploaded_data)
    
    # Render each recommendation with enhanced styling
    for idx, rec in enumerate(recommendations):
        impact = rec.get('impact', 'Medium')
        timeframe = rec.get('timeframe', 'This Week')
        category = rec.get('category', 'General')
        title = rec.get('title', 'Recommendation')
        description = rec.get('description', '')
        
        # Determine styling based on impact
        if impact == 'High':
            impact_class = 'rec-card-high'
            badge_class = 'rec-badge-high'
            impact_emoji = '🔴'
        elif impact == 'Medium':
            impact_class = 'rec-card-medium'
            badge_class = 'rec-badge-medium'
            impact_emoji = '🟠'
        else:
            impact_class = 'rec-card-low'
            badge_class = 'rec-badge-low'
            impact_emoji = '🟢'
        
        # Render recommendation card
        st.markdown(f"""
        <div class="rec-card {impact_class}">
            <div class="rec-title">
                <span>{title}</span>
            </div>
            <div class="rec-badges">
                <span class="rec-badge {badge_class}">{impact_emoji} {impact} Impact</span>
                <span class="rec-badge rec-badge-timeframe">⏱️ {timeframe}</span>
                <span class="rec-category">{category}</span>
            </div>
            <p class="rec-description">{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #1A1A1A; padding: 12px; border-radius: 8px; border-left: 3px solid #6366F1;">
        <p style="font-size: 12px; color: #9CA3AF; margin: 0;">
            <strong>💡 Pro Tip:</strong> Upload your own data on the <strong>Upload Data</strong> page for personalized AI-driven recommendations tailored to your business metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)
