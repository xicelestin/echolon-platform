"""Anomalies & Alerts Detection Page
Provides anomaly detection and smart alerting for business metrics.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_anomalies_alerts_page(data, kpis, format_currency, format_percentage, format_number):
    """Render Anomalies & Alerts Detection page"""
    
    st.title("⚠️ Anomalies & Smart Alerts")
    st.markdown("### AI-powered detection of unusual patterns and business alerts")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload data to view anomaly detection.")
        return
    
    # Alert Summary
    col1, col2, col3, col4 = st.columns(4)
    
    # Detect anomalies (simplified)
    anomalies_count = 0
    critical_alerts = 0
    warnings = 0
    
    if 'revenue' in data.columns:
        revenue_mean = data['revenue'].mean()
        revenue_std = data['revenue'].std()
        anomalies = data[abs(data['revenue'] - revenue_mean) > 2 * revenue_std]
        anomalies_count = len(anomalies)
        critical_alerts = len(anomalies[anomalies['revenue'] < revenue_mean])
        warnings = len(anomalies[anomalies['revenue'] > revenue_mean])
    
    with col1:
        st.metric("Total Anomalies", format_number(anomalies_count))
    
    with col2:
        st.metric("🔴 Critical Alerts", format_number(critical_alerts))
    
    with col3:
        st.metric("🟡 Warnings", format_number(warnings))
    
    with col4:
        health_score = max(0, 100 - (critical_alerts * 10) - (warnings * 5))
        st.metric("🎯 Health Score", f"{health_score}%")
    
    st.markdown("---")
    
    # Anomaly Visualization
    st.subheader("📉 Revenue Anomaly Detection")
    
    if 'revenue' in data.columns and 'date' in data.columns:
        # Calculate rolling statistics
        data_copy = data.copy()
        data_copy['rolling_mean'] = data_copy['revenue'].rolling(window=7).mean()
        data_copy['rolling_std'] = data_copy['revenue'].rolling(window=7).std()
        data_copy['upper_bound'] = data_copy['rolling_mean'] + 2 * data_copy['rolling_std']
        data_copy['lower_bound'] = data_copy['rolling_mean'] - 2 * data_copy['rolling_std']
        
        # Flag anomalies
        data_copy['is_anomaly'] = ((data_copy['revenue'] > data_copy['upper_bound']) | 
                                   (data_copy['revenue'] < data_copy['lower_bound']))
        
        fig = go.Figure()
        
        # Normal data points
        normal_data = data_copy[~data_copy['is_anomaly']]
        fig.add_trace(go.Scatter(x=normal_data['date'], y=normal_data['revenue'],
                                mode='markers', name='Normal',
                                marker=dict(color='blue', size=6)))
        
        # Anomaly points
        anomaly_data = data_copy[data_copy['is_anomaly']]
        fig.add_trace(go.Scatter(x=anomaly_data['date'], y=anomaly_data['revenue'],
                                mode='markers', name='Anomaly',
                                marker=dict(color='red', size=10, symbol='x')))
        
        # Bounds
        fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['rolling_mean'],
                                mode='lines', name='Mean',
                                line=dict(color='green', dash='dash')))
        fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['upper_bound'],
                                mode='lines', name='Upper Bound',
                                line=dict(color='gray', dash='dot'),
                                showlegend=False))
        fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['lower_bound'],
                                mode='lines', name='Lower Bound',
                                line=dict(color='gray', dash='dot'),
                                fill='tonexty', fillcolor='rgba(200, 200, 200, 0.2)'))
        
        fig.update_layout(title='Revenue with Anomaly Detection',
                         xaxis_title='Date', yaxis_title='Revenue')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ Upload data with 'revenue' column to see anomaly detection.")
    
    st.markdown("---")
    
    # Recent Alerts
    st.subheader("📢 Recent Alerts")
    
    alerts = []
    
    # Revenue alerts
    if 'revenue' in data.columns:
        recent_revenue = data['revenue'].tail(7).mean()
        prev_revenue = data['revenue'].iloc[-14:-7].mean() if len(data) >= 14 else recent_revenue
        revenue_change = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        if revenue_change < -15:
            alerts.append({
                'Severity': '🔴 Critical',
                'Category': 'Revenue',
                'Message': f'Revenue dropped {abs(revenue_change):.1f}% in last 7 days',
                'Action': 'Review pricing and marketing campaigns',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
        elif revenue_change < -5:
            alerts.append({
                'Severity': '🟡 Warning',
                'Category': 'Revenue',
                'Message': f'Revenue declined {abs(revenue_change):.1f}% recently',
                'Action': 'Monitor trends closely',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
    
    # Inventory alerts
    if 'inventory_units' in data.columns:
        current_stock = data['inventory_units'].iloc[-1]
        avg_stock = data['inventory_units'].mean()
        
        if current_stock < avg_stock * 0.3:
            alerts.append({
                'Severity': '🔴 Critical',
                'Category': 'Inventory',
                'Message': f'Stock critically low: {format_number(current_stock)} units',
                'Action': 'Expedite reorder immediately',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
        elif current_stock < avg_stock * 0.6:
            alerts.append({
                'Severity': '🟡 Warning',
                'Category': 'Inventory',
                'Message': f'Stock below reorder point',
                'Action': 'Initiate reorder process',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
    
    # Margin alerts
    if 'profit_margin' in data.columns:
        recent_margin = data['profit_margin'].tail(7).mean()
        
        if recent_margin < 15:
            alerts.append({
                'Severity': '🟡 Warning',
                'Category': 'Profitability',
                'Message': f'Profit margin below target: {recent_margin:.1f}%',
                'Action': 'Review costs and pricing strategy',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
    
    if alerts:
        alerts_df = pd.DataFrame(alerts)
        st.dataframe(alerts_df, use_container_width=True)
    else:
        st.success("✅ No active alerts - All metrics within normal ranges")
    
    st.markdown("---")
    
    # Alert Configuration
    st.subheader("⚙️ Alert Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Threshold Configuration**")
        revenue_threshold = st.slider("Revenue Drop Alert (%)", 5, 30, 15)
        margin_threshold = st.slider("Margin Alert (%)", 10, 30, 15)
    
    with col2:
        st.markdown("**Notification Preferences**")
        st.checkbox("Email Notifications", value=True)
        st.checkbox("Dashboard Alerts", value=True)
        st.checkbox("Daily Summary Report", value=False)
    
    st.markdown("---")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    st.info("""**Best Practices:**
    - 🔔 **Set Realistic Thresholds**: Balance sensitivity vs. false positives
    - 📅 **Regular Review**: Check alerts daily during business hours
    - 🤖 **Automate Actions**: Set up automated responses for critical alerts
    - 📊 **Track Trends**: Monitor alert frequency over time
    """)
