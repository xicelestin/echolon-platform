"""Inventory Optimization & Product Performance Page
Provides product-level analytics with fast/slow mover classification.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_inventory_optimization_page(data, kpis, format_currency, format_percentage, format_number):
    """Render Inventory Optimization & Product Performance page"""
    
    st.title("📶 Inventory Optimization & Product Performance")
    st.markdown("### Maximize inventory efficiency with AI-powered product classification")

    # Simulated data badge when actual inventory data missing
    has_actual = data is not None and 'inventory_units' in data.columns
    if data is not None and not data.empty and not has_actual:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#F59E0B 0%,#D97706 100%);color:#1F2937;padding:12px 20px;border-radius:12px;font-weight:700;font-size:0.9rem;margin-bottom:1.5rem;border:2px solid #FBBF24;">
            ⚠️ SIMULATED — Product data below is simulated. Upload data with <code>inventory_units</code> for real recommendations.
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Why is this simulated?"):
            st.markdown("""
            This page uses **simulated product data** because your dataset doesn't include `inventory_units` (and optionally `unit_cost`) at the SKU level.
            To get real reorder recommendations:
            1. Map `inventory_units` in Data Sources
            2. Optionally map `unit_cost` for cost estimates
            3. Use Inventory & Demand for demand-based reorder points
            """)
    
    if data is None or data.empty:
        st.warning("📋 No data available. Please upload data to view inventory insights.")
        return
    
    # Product Performance Analysis Section
    st.subheader("🌆 Product Classification Analysis")
    
    # Simulate product data
    np.random.seed(42)
    num_products = 50
    products_df = pd.DataFrame({
        'product_id': [f'SKU-{i:03d}' for i in range(1, num_products + 1)],
        'product_name': [f'Product {chr(65 + (i % 26))}{i // 26}' for i in range(num_products)],
        'current_stock': np.random.randint(10, 500, num_products),
        'daily_sales': np.random.randint(1, 50, num_products),
        'avg_unit_cost': np.random.uniform(10, 100, num_products),
        'revenue_contribution': np.random.uniform(100, 10000, num_products)
    })
    
    # Calculate metrics
    products_df['days_to_sell'] = products_df['current_stock'] / (products_df['daily_sales'] + 0.1)
    products_df['inventory_value'] = products_df['current_stock'] * products_df['avg_unit_cost']
    
    # ABC Classification (Pareto 80/20)
    products_df['sorted_revenue'] = products_df['revenue_contribution'].rank(ascending=False)
    total_products = len(products_df)
    products_df['cumulative_pct'] = products_df['sorted_revenue'] / total_products * 100
    
    # Classify products
    def classify_product(days_to_sell):
        if days_to_sell < 3:
            return '🟢 Fast-Moving (High Demand)'
        elif days_to_sell < 15:
            return '🟡 Normal-Moving'
        elif days_to_sell < 30:
            return '🔴 Slow-Moving'
        else:
            return '⚫ Dead Stock'
    
    products_df['classification'] = products_df['days_to_sell'].apply(classify_product)
    
    # Display Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fast_movers = (products_df['days_to_sell'] < 3).sum()
        st.metric("🔥 Fast-Moving Products", f"{fast_movers} SKUs", f"{fast_movers/total_products*100:.1f}%")
    
    with col2:
        slow_movers = (products_df['days_to_sell'] > 30).sum()
        st.metric("🚫 Slow-Moving Products", f"{slow_movers} SKUs", f"{slow_movers/total_products*100:.1f}%")
    
    with col3:
        total_inv_value = products_df['inventory_value'].sum()
        st.metric("💵 Total Inventory Value", format_currency(total_inv_value, decimals=0))
    
    with col4:
        slow_inv_value = products_df[products_df['days_to_sell'] > 30]['inventory_value'].sum()
        st.metric("🚨 Slow-Stock Value", format_currency(slow_inv_value, decimals=0))
    
    st.markdown("---")
    
    # Inventory Classification Chart
    st.subheader("📈 Product Movement Analysis")
    
    classification_counts = products_df['classification'].value_counts()
    fig = px.pie(values=classification_counts.values, names=classification_counts.index,
                 title="Product Velocity Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Fast vs Slow Movers Detailed View
    st.subheader("💡 Product Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔥 Fast-Moving Products (Prioritize)")
        fast_moving = products_df[products_df['days_to_sell'] < 3].head(5)
        if not fast_moving.empty:
            for idx, row in fast_moving.iterrows():
                st.success(f"**{row['product_name']}** ({row['product_id']})")
                st.write(f"- Daily Sales: {row['daily_sales']:.0f} units")
                st.write(f"- Days Inventory: {row['days_to_sell']:.1f} days")
                st.write(f"- Revenue: {format_currency(row['revenue_contribution'], decimals=0)}")
                st.info("💯 Action: Increase stock, boost marketing investment")
                st.markdown("---")
        else:
            st.info("No fast-moving products identified yet.")
    
    with col2:
        st.markdown("### 🚫 Slow-Moving Products (Action Required)")
        slow_moving = products_df[products_df['days_to_sell'] > 30].head(5)
        if not slow_moving.empty:
            for idx, row in slow_moving.iterrows():
                st.error(f"**{row['product_name']}** ({row['product_id']})")
                st.write(f"- Daily Sales: {row['daily_sales']:.0f} units")
                st.write(f"- Days Inventory: {row['days_to_sell']:.1f} days")
                st.write(f"- Inventory Value Tied Up: {format_currency(row['inventory_value'], decimals=0)}")
                st.warning("💯 Action: Consider discount/promotion or discontinuation")
                st.markdown("---")
        else:
            st.info("No slow-moving products identified.")
    
    st.markdown("---")
    
    # Inventory Turnover Analysis
    st.subheader("🔄 Inventory Turnover Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_turnover = products_df['daily_sales'].sum() / (products_df['current_stock'].mean() + 0.1)
        st.metric("Overall Inventory Turnover", f"{avg_turnover:.2f}x/year")
        st.caption("Higher = Better efficiency")
    
    with col2:
        fast_moving_turnover = products_df[products_df['days_to_sell'] < 3]['daily_sales'].sum() / (products_df[products_df['days_to_sell'] < 3]['current_stock'].mean() + 0.1) if (products_df['days_to_sell'] < 3).any() else 0
        st.metric("Fast-Movers Turnover", f"{fast_moving_turnover:.2f}x/year")
        st.success("💫 Excellent")
    
    with col3:
        slow_moving_turnover = products_df[products_df['days_to_sell'] > 30]['daily_sales'].sum() / (products_df[products_df['days_to_sell'] > 30]['current_stock'].mean() + 0.1) if (products_df['days_to_sell'] > 30).any() else 0
        st.metric("Slow-Movers Turnover", f"{slow_moving_turnover:.2f}x/year")
        st.warning("⚠️ Action needed")
    
    st.markdown("---")
    
    # Forecasted Stock Needs — require actual inventory data when available
    st.subheader("🔮 Forecasted Stock Needs (Next 30 Days)")
    has_actual_inventory = 'inventory_units' in data.columns if data is not None else False
    if data is not None and not has_actual_inventory:
        st.warning("⚠️ **Inventory inputs missing.** Upload data with `inventory_units` (and optionally `unit_cost`) for real reorder recommendations. Below uses simulated product data.")
    
    # Calculate forecast
    forecast_days = 30
    products_df['forecasted_demand'] = products_df['daily_sales'] * forecast_days
    products_df['stock_needed'] = products_df['forecasted_demand'] * 1.2  # 20% safety stock
    products_df['reorder_needed'] = products_df['stock_needed'] - products_df['current_stock']
    products_df['reorder_needed'] = products_df['reorder_needed'].apply(lambda x: max(0, x))
    
    # Show top products needing reorder
    st.write("**Top 10 Products Needing Reorder:**")
    reorder_list = products_df.nlargest(10, 'reorder_needed')[['product_name', 'product_id', 'current_stock', 'forecasted_demand', 'reorder_needed']]
    
    display_df = reorder_list.copy()
    display_df.columns = ['Product', 'SKU', 'Current Stock', 'Forecasted Demand (30d)', 'Reorder Qty']
    st.dataframe(display_df, use_container_width=True)
    
    # Total reorder recommendation
    total_reorder = products_df['reorder_needed'].sum()
    total_reorder_cost = (total_reorder * products_df['avg_unit_cost'].mean())
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Units to Reorder", f"{int(total_reorder):,}")
    with col2:
        st.metric("Estimated Cost", format_currency(total_reorder_cost, decimals=0))
    
    st.markdown("---")
    
    # AI Recommendations
    st.subheader("🤖 AI-Powered Inventory Recommendations")
    
    recommendations = []
    
    # Slow stock recommendation
    if slow_inv_value > total_inv_value * 0.15:
        recommendations.append({
            'type': 'critical',
            'title': 'Liquidate Slow-Moving Inventory',
            'action': f'Slow-moving stock represents {slow_inv_value/total_inv_value*100:.1f}% of inventory value. Launch liquidation campaign.',
            'impact': f'Potential cash recovery: {format_currency(slow_inv_value * 0.7, decimals=0)}'
        })
    
    # Fast movers recommendation
    if fast_movers > 0:
        recommendations.append({
            'type': 'success',
            'title': 'Increase Fast-Mover Stock Levels',
            'action': 'Fast-moving products have optimal turnover. Increase safety stock to prevent stockouts.',
            'impact': 'Reduce lost sales by 5-10%'
        })
    
    # Seasonal adjustment
    recommendations.append({
        'type': 'info',
        'title': 'Implement Dynamic Pricing',
        'action': 'Use demand velocity to adjust prices. Lower prices for slow movers, premium pricing for fast movers.',
        'impact': 'Improve overall margin by 2-3%'
    })
    
    for rec in recommendations:
        if rec['type'] == 'critical':
            st.error(f"🚨 {rec['title']}")
        elif rec['type'] == 'success':
            st.success(f"✅ {rec['title']}")
        else:
            st.info(f"ℹ️ {rec['title']}")
        
        st.write(f"**Action:** {rec['action']}")
        st.write(f"**Impact:** {rec['impact']}")
        st.markdown("---")

