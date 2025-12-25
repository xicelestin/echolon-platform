"""Inventory & Demand Forecasting Page
Provides inventory tracking, demand forecasting, and stock optimization.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_inventory_demand_page(data, kpis, format_currency, format_percentage, format_number):
    """Render Inventory & Demand Forecasting page"""
    
    st.title("📊 Inventory & Demand Forecasting")
    st.markdown("### Optimize stock levels with AI-powered demand predictions")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload data to view inventory insights.")
        return
    
    # Inventory KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'inventory_units' in data.columns:
            current_stock = data['inventory_units'].iloc[-1]
            st.metric("Current Stock", f"{format_number(current_stock)} units")
        else:
            st.metric("Current Stock", "N/A")
    
    with col2:
        if 'inventory_units' in data.columns:
            avg_stock = data['inventory_units'].mean()
            st.metric("Avg Stock Level", f"{format_number(avg_stock)} units")
        else:
            st.metric("Avg Stock Level", "N/A")
    
    with col3:
        if 'orders' in data.columns:
            avg_daily_demand = data['orders'].mean()
            st.metric("Avg Daily Demand", f"{format_number(avg_daily_demand)} orders")
        else:
            st.metric("Avg Daily Demand", "N/A")
    
    with col4:
        if 'inventory_units' in data.columns and 'orders' in data.columns:
            days_coverage = current_stock / avg_daily_demand if avg_daily_demand > 0 else 0
            st.metric("Days of Stock", f"{days_coverage:.1f} days")
        else:
            st.metric("Days of Stock", "N/A")
    
    st.markdown("---")
    
    # Stock Level Visualization
    st.subheader("📊 Stock Levels Over Time")
    
    if 'inventory_units' in data.columns and 'date' in data.columns:
        # Calculate thresholds
        avg_inventory = data['inventory_units'].mean()
        reorder_point = avg_inventory * 0.6
        safety_stock = avg_inventory * 0.3
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['date'], y=data['inventory_units'],
                                mode='lines', name='Stock Level',
                                fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.3)'))
        fig.add_hline(y=reorder_point, line_dash="dash", line_color="orange",
                     annotation_text="Reorder Point")
        fig.add_hline(y=safety_stock, line_dash="dash", line_color="red",
                     annotation_text="Safety Stock")
        fig.update_layout(title='Inventory Levels with Thresholds',
                         xaxis_title='Date', yaxis_title='Units')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ Upload data with 'inventory_units' column to see stock trends.")
    
    st.markdown("---")
    
    # Demand Forecasting
    st.subheader("🔮 Demand Forecast (Next 30 Days)")
    
    if 'orders' in data.columns and 'date' in data.columns:
        # Simple linear forecast
        recent_orders = data['orders'].tail(30)
        avg_demand = recent_orders.mean()
        trend = (recent_orders.iloc[-1] - recent_orders.iloc[0]) / 30
        
        # Forecast next 30 days
        forecast_days = 30
        last_date = data['date'].max()
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1),
                                      periods=forecast_days, freq='D')
        forecast_values = [avg_demand + (trend * i) for i in range(forecast_days)]
        
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'forecasted_demand': forecast_values
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['date'], y=data['orders'],
                                mode='lines', name='Historical Demand',
                                line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['forecasted_demand'],
                                mode='lines', name='Forecasted Demand',
                                line=dict(color='red', dash='dash')))
        fig.update_layout(title='Demand Forecast',
                         xaxis_title='Date', yaxis_title='Orders')
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            total_forecast = sum(forecast_values)
            st.metric("Predicted Orders (30d)", f"{format_number(total_forecast)} orders")
        with col2:
            avg_forecast = np.mean(forecast_values)
            st.metric("Avg Daily Forecast", f"{format_number(avg_forecast)} orders/day")
        with col3:
            trend_pct = (trend / avg_demand * 100) if avg_demand > 0 else 0
            st.metric("Demand Trend", f"{trend_pct:+.1f}%")
    else:
        st.info("ℹ️ Upload data with 'orders' column to see demand forecast.")
    
    st.markdown("---")
    
    # Stock Recommendations
    st.subheader("🎯 Restocking Recommendations")
    
    if 'inventory_units' in data.columns and 'orders' in data.columns:
        recommendations = []
        
        current_stock = data['inventory_units'].iloc[-1]
        avg_daily_demand = data['orders'].mean()
        reorder_point = avg_inventory * 0.6
        optimal_stock = avg_inventory * 1.2
        
        if current_stock < reorder_point:
            needed = optimal_stock - current_stock
            recommendations.append({
                'priority': '🔴 High',
                'action': f'Reorder Now',
                'quantity': f"{format_number(needed)} units",
                'reason': 'Stock below reorder point'
            })
        elif current_stock < avg_inventory:
            needed = optimal_stock - current_stock
            recommendations.append({
                'priority': '🟡 Medium',
                'action': f'Plan Reorder',
                'quantity': f"{format_number(needed)} units",
                'reason': 'Stock below average'
            })
        else:
            recommendations.append({
                'priority': '🟢 Low',
                'action': 'Monitor',
                'quantity': 'N/A',
                'reason': 'Stock levels healthy'
            })
        
        rec_df = pd.DataFrame(recommendations)
        st.table(rec_df)
    
    # Actionable Insights
    st.markdown("---")
    st.subheader("💡 Key Insights")
    
    st.info("""**Optimization Tips:**
    - 📊 **Lead Time**: Account for 5-7 days supplier lead time
    - 💰 **Holding Costs**: Minimize excess inventory to reduce costs
    - 🚀 **Demand Spikes**: Prepare for seasonal variations
    - ✅ **Auto-Reorder**: Set up automated reorder triggers at reorder point
    """)
