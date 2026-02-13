"""Margin Analysis & Profitability Page
Comprehensive profitability analysis with product and segment breakdowns.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_margin_analysis_page(data, kpis, format_currency, format_percentage, format_number):
    """Render Margin Analysis & Profitability page"""
    
    st.title("📈 Margin Analysis & Profitability")
    st.markdown("### Deep insights into profitability drivers and optimization opportunities")
    
    if data is None or data.empty:
        st.warning("📋 No data available. Please upload data to view margin analysis.")
        return
    
    # Calculate margin metrics
    total_revenue = data['revenue'].sum() if 'revenue' in data.columns else 0
    total_cost = data['cost'].sum() if 'cost' in data.columns else total_revenue * 0.6
    total_profit = total_revenue - total_cost
    
    gross_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    cogs_percent = (total_cost / total_revenue * 100) if total_revenue > 0 else 0
    
    # Display Profitability Overview
    st.subheader("🌐 Profitability Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", format_currency(total_revenue, decimals=1))
    with col2:
        st.metric("Total Cost", format_currency(total_cost, decimals=1))
    with col3:
        st.metric("Total Profit", format_currency(total_profit, decimals=1))
    with col4:
        status = "✅ Healthy" if gross_margin > 30 else ("⚠️ Average" if gross_margin > 20 else "🚨 Low")
        st.metric("Gross Margin", format_percentage(gross_margin), status)
    
    st.markdown("---")
    
    # Waterfall Chart: Revenue to Profit
    st.subheader("🌪 Profit Waterfall")
    
    waterfall_data = {
        'Stage': ['Revenue', 'COGS', 'Gross Profit', 'OpEx', 'Net Profit'],
        'Amount': [total_revenue, -total_cost, total_profit, -total_profit*0.2, total_profit*0.8]
    }
    
    fig = go.Figure(go.Waterfall(
        x=waterfall_data['Stage'],
        y=waterfall_data['Amount'],
        connector={"line": {"color": "rgba(63, 63, 63, 0.5)"}},
    ))
    fig.update_layout(title="Revenue Flow to Net Profit")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Margin Trends
    st.subheader("📈 Margin Trends Analysis")
    
    data_copy = data.copy()
    if 'profit' in data_copy.columns:
        data_copy['margin_pct'] = (data_copy['profit'] / (data_copy['revenue'] + 0.01) * 100)
    else:
        data_copy['margin_pct'] = ((data_copy['revenue'] - data_copy['cost']) / (data_copy['revenue'] + 0.01) * 100)
    
    if 'date' in data_copy.columns:
        fig = px.line(data_copy, x='date', y='margin_pct',
                      title='Daily Profit Margin Trend')
        fig.add_hline(y=gross_margin, line_dash="dash", line_color="green",
                     annotation_text="Average Margin")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Margin by Category (real data when category exists, else simulated)
    st.subheader("📊 Margin by Product Category")
    
    if 'category' in data.columns:
        cat_agg = data.groupby('category')['revenue'].sum().reset_index()
        if 'profit' in data.columns:
            cat_profit = data.groupby('category')['profit'].sum().reset_index()
            cat_agg = cat_agg.merge(cat_profit, on='category')
            cat_agg['margin_pct'] = (cat_agg['profit'] / cat_agg['revenue'] * 100).round(1)
        else:
            margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
            cat_agg['margin_pct'] = margin
        categories = cat_agg['category'].tolist()
        margins_by_category = dict(zip(cat_agg['category'], cat_agg['margin_pct']))
        revenue_by_category = dict(zip(cat_agg['category'], cat_agg['revenue']))
    else:
        categories = ['Electronics', 'Software', 'Services', 'Consulting', 'Support']
        margins_by_category = {'Electronics': 15, 'Software': 85, 'Services': 45, 'Consulting': 65, 'Support': 55}
        revenue_by_category = {c: total_revenue * (0.30 if c == 'Electronics' else 0.25 if c == 'Software' else 0.20 if c == 'Services' else 0.15 if c == 'Consulting' else 0.10) for c in categories}
    
    margin_df = pd.DataFrame({
        'Category': list(margins_by_category.keys()),
        'Margin %': list(margins_by_category.values()),
        'Revenue': list(revenue_by_category.values())
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(margin_df, x='Category', y='Margin %',
                    color='Margin %', color_continuous_scale='RdYlGn',
                    title='Profit Margin by Category')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(margin_df, values='Revenue', names='Category',
                    title='Revenue Distribution by Category')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Pricing Optimization Recommendations
    st.subheader("🤖 AI Pricing Optimization Recommendations")
    
    recommendations = []
    
    # Find low-margin products
    low_margin_cats = [cat for cat, margin in margins_by_category.items() if margin < 25]
    if low_margin_cats:
        recommendations.append({
            'type': 'warning',
            'title': f'Increase Prices for {low_margin_cats[0]}',
            'action': f'{low_margin_cats[0]} has {margins_by_category[low_margin_cats[0]]}% margin. A 10-15% price increase is justified.',
            'impact': f'Revenue increase: {format_currency(revenue_by_category[low_margin_cats[0]] * 0.12, decimals=0)}'
        })
    
    # High-margin opportunity
    high_margin_cats = [cat for cat, margin in margins_by_category.items() if margin > 60]
    if high_margin_cats:
        recommendations.append({
            'type': 'success',
            'title': f'Expand {high_margin_cats[0]} Offerings',
            'action': f'{high_margin_cats[0]} has {margins_by_category[high_margin_cats[0]]}% margin. Increase marketing investment.',
            'impact': 'Potential profit increase: $500K-$1M'
        })
    
    # Cost reduction opportunity
    if cogs_percent > 70:
        recommendations.append({
            'type': 'critical',
            'title': 'Optimize Cost Structure',
            'action': f'COGS is {cogs_percent:.1f}% of revenue. Negotiate supplier contracts and improve processes.',
            'impact': f'Potential margin improvement: 3-5 percentage points'
        })
    
    for rec in recommendations:
        if rec['type'] == 'critical':
            st.error(f"🚨 {rec['title']}")
        elif rec['type'] == 'success':
            st.success(f"✅ {rec['title']}")
        else:
            st.warning(f"⚠️ {rec['title']}")
        
        st.write(f"**Action:** {rec['action']}")
        st.write(f"**Impact:** {rec['impact']}")
        st.markdown("---")
    
    # Unit Economics
    st.subheader("💵 Unit Economics & Scalability")
    
    total_units = data['orders'].sum() if 'orders' in data.columns else 0
    cogs_per_unit = total_cost / (total_units + 1) if total_units > 0 else 0
    revenue_per_unit = total_revenue / (total_units + 1) if total_units > 0 else 0
    profit_per_unit = revenue_per_unit - cogs_per_unit
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Units Sold", format_number(int(total_units)))
    with col2:
        st.metric("Revenue per Unit", format_currency(revenue_per_unit, decimals=2))
    with col3:
        st.metric("COGS per Unit", format_currency(cogs_per_unit, decimals=2))
    with col4:
        st.metric("Profit per Unit", format_currency(profit_per_unit, decimals=2))
    
    st.markdown("---")
    
    # Breakeven Analysis
    st.subheader("🚯 Breakeven Analysis")
    
    fixed_costs = total_cost * 0.30  # Assume 30% fixed
    variable_cost_per_unit = cogs_per_unit
    contribution_margin = revenue_per_unit - variable_cost_per_unit
    
    if contribution_margin > 0:
        breakeven_units = fixed_costs / contribution_margin
        breakeven_revenue = breakeven_units * revenue_per_unit
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Breakeven Units", f"{int(breakeven_units):,}")
        with col2:
            st.metric("Breakeven Revenue", format_currency(breakeven_revenue, decimals=0))
        with col3:
            safety_margin = ((total_revenue - breakeven_revenue) / total_revenue * 100)
            st.metric("Safety Margin", format_percentage(safety_margin))

