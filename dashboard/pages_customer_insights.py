"""Customer Insights & Segmentation Page
Provides customer analytics, segmentation, and behavioral insights.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_customer_insights_page(data, kpis, format_currency, format_percentage, format_number):
    """Render Customer Insights & Segmentation page"""
    
    st.title("👥 Customer Insights & Segmentation")
    st.markdown("### Deep dive into customer behavior and segments")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload data to view customer insights.")
        return
    
    # Customer KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = kpis.get('total_customers', 0)
        st.metric("Total Customers", format_number(total_customers))
    
    with col2:
        new_customers = data['new_customers'].sum() if 'new_customers' in data.columns else 0
        st.metric("New Customers", format_number(new_customers))
    
    with col3:
        avg_ltv = kpis.get('avg_order_value', 0) * 3  # Simplified LTV
        st.metric("Avg Customer LTV", format_currency(avg_ltv, 0))
    
    with col4:
        retention_rate = 75.0  # Placeholder
        st.metric("Retention Rate", format_percentage(retention_rate))
    
    st.markdown("---")
    
    # Customer Segmentation
    st.subheader("📊 Customer Segmentation")
    
    # Simulate customer segments
    segments = pd.DataFrame({
        'Segment': ['High Value', 'Medium Value', 'Low Value', 'At Risk'],
        'Count': [500, 1200, 800, 300],
        'Avg Revenue': [5000, 2000, 500, 200],
        'Retention': [95, 80, 60, 30]
    })
    
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
