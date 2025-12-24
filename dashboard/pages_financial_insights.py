"""Financial & Cash Flow Insights Page
Provides comprehensive financial analysis including cash flow, margins, and profitability.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_financial_page(data, kpis, format_currency, format_percentage, format_number):
    """Render Financial & Cash Flow Insights page"""
    
    st.title("💰 Financial & Cash Flow Insights")
    st.markdown("### Comprehensive financial analysis with AI-powered recommendations")
    
    if data is None or data.empty:
        st.warning("📊 No data available. Please upload data to view financial insights.")
        return
    
    # Calculate financial metrics
    total_revenue = data['revenue'].sum() if 'revenue' in data.columns else 0
    total_cost = data['cost'].sum() if 'cost' in data.columns else total_revenue * 0.6
    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Cash flow calculations
    data_copy = data.copy()
    if 'date' in data_copy.columns:
        data_copy['date'] = pd.to_datetime(data_copy['date'])
        data_copy['operating_cash_flow'] = data_copy['profit'] if 'profit' in data_copy.columns else (data_copy['revenue'] - data_copy['cost'])
        data_copy['cumulative_cash'] = data_copy['operating_cash_flow'].cumsum()
    
    # Page 1: Cash Flow Overview
    st.subheader("📊 Cash Flow Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'operating_cash_flow' in data_copy.columns:
            ocf = data_copy['operating_cash_flow'].sum()
            st.metric("Operating Cash Flow", format_currency(ocf, decimals=1))
    
    with col2:
        current_cash = data_copy['cumulative_cash'].iloc[-1] if 'cumulative_cash' in data_copy.columns else 0
        st.metric("Cumulative Cash Position", format_currency(current_cash, decimals=1))
    
    with col3:
        monthly_burn = (total_cost / 12) if total_cost > 0 else 0
        st.metric("Monthly Burn Rate", format_currency(monthly_burn, decimals=1))
    
    with col4:
        cash_runway = current_cash / monthly_burn if monthly_burn > 0 else float('inf')
        runway_status = "✅ Healthy" if cash_runway > 12 else ("⚠️ Caution" if cash_runway > 6 else "🚨 Critical")
        st.metric("Cash Runway (months)", f"{min(cash_runway, 99):.1f}", runway_status)
    
    st.markdown("---")
    
    # Cash Flow Chart
    st.subheader("📈 Cash Flow Trend")
    if 'date' in data_copy.columns and 'operating_cash_flow' in data_copy.columns:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=data_copy['date'], y=data_copy['operating_cash_flow'], name='Daily Cash Flow'))
        fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['cumulative_cash'], 
                                 mode='lines', name='Cumulative Cash', line=dict(color='red', width=3)))
        fig.update_layout(title='Operating Cash Flow & Cumulative Position',
                         xaxis_title='Date', yaxis_title='Amount ($)',
                         hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Working Capital Analysis
    st.subheader("💼 Working Capital Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    # DPO (Days Payable Outstanding)
    with col1:
        dpo = 45  # Simplified for demo
        st.metric("Days Payable Outstanding (DPO)", f"{dpo} days")
        st.caption("Average time to pay suppliers")
    
    # DIO (Days Inventory Outstanding)
    with col2:
        if 'inventory_units' in data.columns and 'orders' in data.columns:
            avg_inventory = data['inventory_units'].mean()
            avg_daily_sales = data['orders'].mean()
            dio = (avg_inventory / avg_daily_sales * 365) if avg_daily_sales > 0 else 0
            st.metric("Days Inventory Outstanding (DIO)", f"{dio:.0f} days")
            st.caption("Average inventory holding period")
    
    # DSO (Days Sales Outstanding)
    with col3:
        dso = 30  # Simplified for demo
        st.metric("Days Sales Outstanding (DSO)", f"{dso} days")
        st.caption("Average time to collect from customers")
    
    st.info(f"""**Cash Conversion Cycle:** {(dpo - dio - dso):.0f} days
    - Positive = Working capital tied up (need to finance)
    - Negative = Customers pay before you pay suppliers (efficient!)
    """)
    
    st.markdown("---")
    
    # Financial Health Metrics
    st.subheader("📊 Financial Health Ratios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_ratio = 1.5  # Simplified
        st.metric("Current Ratio", f"{current_ratio:.2f}x")
        st.caption("Target: > 1.5x (Liquid assets vs liabilities)")
        if current_ratio > 1.5:
            st.success("✅ Healthy")
        else:
            st.warning("⚠️ Watch liquidity")
    
    with col2:
        gross_margin = profit_margin
        st.metric("Gross Margin", format_percentage(gross_margin))
        st.caption("Revenue minus cost of goods sold")
        if gross_margin > 40:
            st.success("✅ Strong margins")
        elif gross_margin > 25:
            st.info("ℹ️ Average margins")
        else:
            st.warning("⚠️ Low margins")
    
    with col3:
        roa = (total_profit / (total_revenue * 0.5)) * 100 if total_revenue > 0 else 0
        st.metric("Return on Assets (ROA)", format_percentage(roa))
        st.caption("Profit generated per dollar of assets")
        if roa > 20:
            st.success("✅ Excellent")
        else:
            st.info("ℹ️ Monitor trends")
    
    st.markdown("---")
    
    # AI Recommendations
    st.subheader("🤖 AI Financial Recommendations")
    
    recommendations = []
    
    # Cash flow recommendation
    if cash_runway < 12:
        recommendations.append({
            'type': 'critical',
            'title': 'Improve Cash Runway',
            'action': f'Your cash runway is {cash_runway:.1f} months. Recommend increasing cash reserves or reducing monthly burn rate.',
            'potential_impact': '$' + format(int(monthly_burn * 6), ',')
        })
    
    # Margin recommendation
    if profit_margin < 20:
        recommendations.append({
            'type': 'warning',
            'title': 'Optimize Margins',
            'action': f'Current margin is {profit_margin:.1f}%. Review supplier costs and consider 5-10% price increase.',
            'potential_impact': format_currency(total_revenue * 0.05, decimals=0)
        })
    
    # Profitability recommendation
    if total_profit < 0:
        recommendations.append({
            'type': 'critical',
            'title': 'Address Negative Profitability',
            'action': 'Business is currently unprofitable. Analyze cost structure and pricing strategy immediately.',
            'potential_impact': 'Requires immediate action'
        })
    
    if recommendations:
        for rec in recommendations:
            if rec['type'] == 'critical':
                with st.container():
                    st.error(f"🚨 {rec['title']}")
                    st.write(f"**Action:** {rec['action']}")
                    st.write(f"**Potential Impact:** {rec['potential_impact']}")
            else:
                with st.container():
                    st.warning(f"⚠️ {rec['title']}")
                    st.write(f"**Action:** {rec['action']}")
                    st.write(f"**Potential Impact:** {rec['potential_impact']}")
            st.markdown("---")
    else:
        st.success("✅ All financial metrics are healthy!")
    
    # Cash Flow Forecast
    st.subheader("🔮 Cash Flow Forecast (Next 90 Days)")
    
    forecast_days = 90
    avg_daily_cf = data_copy['operating_cash_flow'].mean() if 'operating_cash_flow' in data_copy.columns else 0
    
    forecast_dates = pd.date_range(start=datetime.now(), periods=forecast_days)
    forecast_cash = [current_cash + (avg_daily_cf * i) for i in range(1, forecast_days + 1)]
    
    forecast_df = pd.DataFrame({
        'date': forecast_dates,
        'projected_cash': forecast_cash
    })
    
    fig = px.line(forecast_df, x='date', y='projected_cash',
                  title='90-Day Cash Flow Forecast')
    fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Cash Depletion")
    st.plotly_chart(fig, use_container_width=True)

