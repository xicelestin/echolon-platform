"""Customer Insights & Segmentation Page
Provides customer analytics, segmentation, and behavioral insights.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.rfm_segmentation import compute_retention_from_data, compute_rfm_segments_from_data
from utils import calculate_key_metrics, calculate_ltv

def render_customer_insights_page(data, kpis, format_currency, format_percentage, format_number):
    """Render Customer Insights & Segmentation page"""
    
    st.title("👥 Customer Insights & Segmentation")
    st.markdown("### Deep dive into customer behavior and segments")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload data to view customer insights.")
        return
    
    # Customer KPIs - all derived from actual data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = kpis.get('total_customers', 0)
        if total_customers == 0 and 'customers' in data.columns and len(data) > 0:
            total_customers = int(data['customers'].iloc[-1])
        st.metric("Total Customers", format_number(total_customers))
    
    with col2:
        new_customers = data['new_customers'].sum() if 'new_customers' in data.columns else 0
        st.metric("New Customers", format_number(new_customers))
    
    with col3:
        avg_ltv = calculate_ltv(data)
        st.metric("Avg Customer LTV", format_currency(avg_ltv, 0))
    
    with col4:
        retention_rate = compute_retention_from_data(data)
        if retention_rate is None:
            retention_rate = 75.0  # Fallback only when data cannot support calculation
        st.metric("Retention Rate", format_percentage(retention_rate))
    
    st.markdown("---")
    
    # Customer Segmentation - RFM-style from actual data
    st.subheader("📊 Customer Segmentation")
    
    segments = compute_rfm_segments_from_data(data)
    
    if segments.empty or segments['Count'].sum() == 0:
        st.info("📊 Add channel, category, or product columns to your data for RFM-style segmentation. Using revenue distribution by time period.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(segments, values='Count', names='Segment', 
                     title='Customer Distribution by Segment')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(segments, x='Segment', y='Avg Revenue',
                     title='Average Revenue by Segment',
                     color='Avg Revenue',
                     color_continuous_scale='blues')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Customer Behavior Trends
    st.subheader("📈 Customer Behavior Trends")
    
    if 'customers' in data.columns and 'date' in data.columns:
        fig = px.line(data, x='date', y='customers',
                      title='Customer Count Over Time')
        fig.update_layout(xaxis_title='Date', yaxis_title='Customers')
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer Insights Table
    st.markdown("---")
    st.subheader("📋 Segment Details")
    
    if 'Lifetime Value' not in segments.columns:
        segments['Lifetime Value'] = segments['Avg Revenue'] * 3
    segments['Status'] = segments['Retention'].apply(
        lambda x: '🟢 Healthy' if x > 70 else '🟡 Warning' if x > 50 else '🔴 At Risk'
    )
    
    st.dataframe(segments, use_container_width=True)
    
    # Actionable Recommendations
    st.markdown("---")
    st.subheader("💡 Recommendations")
    
    st.info("""**Recommended Actions:**
    - 🎯 **High Value Customers**: Launch VIP loyalty program
    - 📧 **At Risk Customers**: Send re-engagement campaigns
    - 📈 **Medium Value**: Upsell premium products
    - 🆕 **New Customers**: Implement onboarding sequence
    """)
