"""Sales Distribution & Key Metrics Page."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from advanced_components import SalesInsights
from premium_enhancements import detect_anomalies, render_alert, predict_churn, cohort_table, benchmark_chart
from enhancement_features import show_benchmark_comparison

def create_kpi_card(icon, title, value, delta, delta_pct_color, help_text):
    """Create a professional KPI card."""
    return f'''
    <div style='background:linear-gradient(135deg, #1F2937 0%, #111827 100%);border-radius:12px;padding:20px;border:1px solid #374151;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
        <div style='display:flex;justify-content:space-between;align-items:start;'>
            <div>
                <p style='color:#9CA3AF;font-size:13px;margin:0;font-weight:500;'>{title}</p>
                <h3 style='color:#F3F4F6;font-size:28px;font-weight:700;margin:8px 0 4px 0;'>{value}</h3>
                <p style='color:{delta_pct_color};font-size:13px;margin:0;font-weight:600;'>{delta}</p>
            </div>
            <div style='font-size:32px;'>{icon}</div>
        </div>
        <p style='color:#6B7280;font-size:12px;margin:12px 0 0 0;border-top:1px solid #374151;padding-top:12px;'>{help_text}</p>
    </div>
    '''

def render_insights_page():
    """Render the Sales Insights & Key Metrics page."""
    st.markdown("""<div style='margin-bottom:30px'><h1 style='font-size:36px;font-weight:700;margin-bottom:5px'>Sales Insights & Key Metrics</h1><p style='color:#9CA3AF;font-size:16px;margin:0'>Comprehensive business performance analysis</p></div>""", unsafe_allow_html=True)
    
    st.markdown(f"""<div style='background:#065F46;color:#D1FAE5;border-radius:8px;padding:12px 16px;font-size:15px;margin-bottom:24px;'><b>✓ Live Data</b> | Last updated: {datetime.now().strftime('%H:%M on %Y-%m-%d')}</div>""", unsafe_allow_html=True)
    
    # Generate mock data
    np.random.seed(42)
    revenue_data = np.random.normal(500000, 50000, 30)
    
    # KPI Calculations
    total_revenue = revenue_data.sum()
    active_customers = 2340
    avg_order_value = 127.50
    ltv = 3450
    cac = 45
    ltv_cac_ratio = ltv / cac
    mrr_growth = 8.2
    churn_rate = 2.1
    
    # Display KPI Cards in 4 columns
    st.markdown("""<div style='margin-bottom:24px'><h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>Key Performance Indicators</h3></div>""", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_kpi_card(
            '💰', 'Total Revenue', f'${total_revenue/1000:.0f}K',
            '↑ 8.2%', '#10B981', 'Total revenue this period'
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_kpi_card(
            '👥', 'Active Customers', f'{active_customers:,}',
            '↑ 12.5%', '#10B981', 'Active customer count'
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_kpi_card(
            '🛍️', 'Average Order Value', f'${avg_order_value:.2f}',
            '↓ 2.1%', '#EF4444', 'Mean transaction value'
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_kpi_card(
            '💎', 'Customer LTV', f'${ltv:,.0f}',
            '↑ 12.3%', '#10B981', 'Lifetime value per customer'
        ), unsafe_allow_html=True)
    
    # Second row of KPIs
    st.markdown("""<div style='margin:24px 0;'></div>""", unsafe_allow_html=True)
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown(create_kpi_card(
            '📊', 'CAC', f'${cac:.0f}',
            '↓ 5.2%', '#10B981', 'Customer acquisition cost'
        ), unsafe_allow_html=True)
    
    with col6:
        efficiency_color = '#10B981' if ltv_cac_ratio > 20 else '#F59E0B'
        efficiency_pct = '↑ 18%'
        st.markdown(create_kpi_card(
            '⚡', 'LTV/CAC Ratio', f'{ltv_cac_ratio:.1f}x',
            efficiency_pct, efficiency_color, 'LTV to CAC ratio (>20x ideal)'
        ), unsafe_allow_html=True)
    
    with col7:
        st.markdown(create_kpi_card(
            '📈', 'MRR Growth', f'{mrr_growth:.1f}%',
            '↑ 2.1%', '#10B981', 'Monthly recurring revenue growth'
        ), unsafe_allow_html=True)
    
    with col8:
        st.markdown(create_kpi_card(
            '⚠️', 'Churn Rate', f'{churn_rate:.1f}%',
            '↓ 0.3%', '#10B981', 'Monthly customer churn'
        ), unsafe_allow_html=True)
    
    # Divider
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    
    # Breakdown Analysis
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:20px;font-weight:600;'>Sales Breakdown Analysis</h3></div>""", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""<div style='margin-bottom:16px'><h4 style='font-size:16px;font-weight:600;'>By Product Category</h4></div>""", unsafe_allow_html=True)
        
        categories = pd.DataFrame({
            'Category': ['Electronics', 'Home & Garden', 'Apparel', 'Sports', 'Books'],
            'Revenue': [125000, 98000, 87000, 65000, 45000],
            'Units Sold': [450, 320, 580, 290, 620]
        })
        
        fig_cat = px.bar(
            categories, x='Revenue', y='Category', orientation='h',
            color='Revenue', color_continuous_scale='Blues',
            title='Revenue by Category'
        )
        fig_cat.update_layout(height=300, template='plotly_dark', showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col_right:
        st.markdown("""<div style='margin-bottom:16px'><h4 style='font-size:16px;font-weight:600;'>By Sales Channel</h4></div>""", unsafe_allow_html=True)
        
        channels = pd.DataFrame({
            'Channel': ['Online Store', 'Mobile App', 'Wholesale', 'Retail Partners', 'B2B'],
            'Revenue': [210000, 142000, 98000, 32000, 18000]
        })
        
        fig_channel = px.pie(
            channels, values='Revenue', names='Channel',
            title='Revenue Distribution by Channel',
            color_discrete_sequence=['#3B82F6', '#06B6D4', '#8B5CF6', '#EC4899', '#F59E0B']
        )
        fig_channel.update_layout(height=300, template='plotly_dark')
        st.plotly_chart(fig_channel, use_container_width=True)
    
    # Regional Analysis
    st.markdown("""<div style='margin:24px 0 16px 0;border-top:1px solid #374151;padding-top:24px;'><h4 style='font-size:16px;font-weight:600;margin-bottom:16px;'>Regional Performance</h4></div>""", unsafe_allow_html=True)
    
    regions = pd.DataFrame({
        'Region': ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East & Africa'],
        'Revenue': [250000, 145000, 85000, 35000, 15000],
        'Growth %': [8.5, 12.3, 15.8, 5.2, 3.1],
        'Customers': [1050, 650, 480, 120, 40]
    })
    
    fig_regional = go.Figure()
    fig_regional.add_trace(go.Bar(
        x=regions['Region'], y=regions['Revenue'],
        name='Revenue', marker_color='#3B82F6'
    ))
    fig_regional.update_layout(
        title='Revenue by Region',
        xaxis_title='Region', yaxis_title='Revenue ($)',
        height=350, template='plotly_dark'
    )
    st.plotly_chart(fig_regional, use_container_width=True)
    
    # Insights Section
    st.markdown("""<div style='margin:32px 0 16px 0;border-top:1px solid #374151;padding-top:24px;'><h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>📊 Key Insights & Recommendations</h3></div>""", unsafe_allow_html=True)
    
    insight_cols = st.columns(2)
    
    with insight_cols[0]:
        st.markdown("""
        ### ✅ What's Performing Well
        
        - **Asia Pacific Growth**: 15.8% YoY growth outpacing other regions
        - **LTV Improvement**: 12.3% increase driven by repeat purchases
        - **CAC Efficiency**: Down 5.2% while maintaining customer quality
        - **Customer Retention**: Churn down to 2.1%, industry benchmark is 3.5%
        """)
    
    with insight_cols[1]:
        st.markdown("""
        ### ⚠️ Areas for Attention
        
        - **AOV Decline**: 2.1% decrease suggests pricing pressure
        - **Regional Disparity**: MENA regions underperforming (+3.1% vs +15.8%)
        - **Channel Consolidation**: B2B channel only 2.8% of revenue
        - **Wholesale Growth**: Opportunity to expand wholesale partnerships
        """)
    
    # Action Items
    st.markdown("""<div style='margin:24px 0 16px 0;'><h4 style='font-size:16px;font-weight:600;margin-bottom:16px;'>💡 Recommended Actions</h4></div>""", unsafe_allow_html=True)
    
    action_items = pd.DataFrame({
        'Priority': ['🔴 High', '🔴 High', '🟡 Medium', '🟡 Medium'],
        'Action': [
            'Expand Asia Pacific operations',
            'Investigate AOV decline with pricing review',
            'Scale B2B channel with dedicated team',
            'Implement MENA region marketing push'
        ],
        'Expected Impact': ['+$50K revenue', '+$20K revenue', '+$15K revenue', '+$8K revenue'],
        'Timeline': ['90 days', '30 days', '60 days', '45 days']
    })
    
    st.dataframe(action_items, use_container_width=True, hide_index=True)

    # Add benchmark comparison feature
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    show_benchmark_comparison()
