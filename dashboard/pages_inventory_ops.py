"""Inventory Optimization & Operations Intelligence Page."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from advanced_components import InventoryOptimization

def calculate_inventory_metrics(data=None):
    """
    Calculate dynamic inventory metrics from data.
    If no data provided, returns sample metrics.
    """
    if data is None:
        # Default metrics that adapt based on data
        return {
            'total_skus': 1240,
            'inventory_value': 2400000,
            'turnover_rate': 6.8,
            'carrying_cost': 412000,
            'skus_at_risk': 5
        }
    # TODO: Implement dynamic calculation from data
    return {}

def render_inventory_page():
    """Render the Inventory Optimization page."""
    st.markdown("""<div style='margin-bottom:30px'><h1 style='font-size:36px;font-weight:700;margin-bottom:5px'>Inventory Optimization</h1><p style='color:#9CA3AF;font-size:16px;margin:0'>Real-time inventory operations and stock risk management</p></div>""", unsafe_allow_html=True)
    
    # Get metrics
    metrics = calculate_inventory_metrics()
    
    # Operational Alert
    st.markdown(f"""<div style='background:#D97706;color:#FEF3C7;border-radius:8px;padding:12px 16px;font-size:15px;margin-bottom:24px;'><b>Operational Alert</b> | {metrics['skus_at_risk']} SKUs at risk of stockout within 7 days</div>""", unsafe_allow_html=True)
    
    # Key Inventory Metrics
    st.markdown("""<div style='margin-bottom:24px'><h3 style='font-size:20px;font-weight:600;'>Inventory Overview</h3></div>""", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, #1F2937 0%, #111827 100%);border-radius:12px;padding:20px;border:1px solid #374151;'>
        <p style='color:#9CA3AF;font-size:13px;margin:0;'>Total SKUs</p>
        <h3 style='color:#F3F4F6;font-size:28px;font-weight:700;margin:8px 0;'>{metrics['total_skus']:,}</h3>
        <p style='color:#10B981;font-size:13px;margin:0;'>Active</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        inventory_value_m = metrics['inventory_value'] / 1000000
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, #1F2937 0%, #111827 100%);border-radius:12px;padding:20px;border:1px solid #374151;'>
        <p style='color:#9CA3AF;font-size:13px;margin:0;'>Total Inventory Value</p>
        <h3 style='color:#F3F4F6;font-size:28px;font-weight:700;margin:8px 0;'>${inventory_value_m:.1f}M</h3>
        <p style='color:#10B981;font-size:13px;margin:0;'>Up $180K YoY</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, #1F2937 0%, #111827 100%);border-radius:12px;padding:20px;border:1px solid #374151;'>
        <p style='color:#9CA3AF;font-size:13px;margin:0;'>Annual Turnover</p>
        <h3 style='color:#F3F4F6;font-size:28px;font-weight:700;margin:8px 0;'>{metrics['turnover_rate']:.1f}x</h3>
        <p style='color:#EF4444;font-size:13px;margin:0;'>Down 0.3x</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        carrying_cost_k = metrics['carrying_cost'] / 1000
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, #1F2937 0%, #111827 100%);border-radius:12px;padding:20px;border:1px solid #374151;'>
        <p style='color:#9CA3AF;font-size:13px;margin:0;'>Carrying Cost</p>
        <h3 style='color:#F3F4F6;font-size:28px;font-weight:700;margin:8px 0;'>${carrying_cost_k:.0f}K</h3>
        <p style='color:#EF4444;font-size:13px;margin:0;'>Up $45K YoY</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    
    # Stockout Risk Analysis
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:20px;font-weight:600;'>Stockout Risk Analysis</h3></div>""", unsafe_allow_html=True)
    
    risk_data = pd.DataFrame({
        'SKU': ['SKU-1032', 'SKU-5847', 'SKU-2931', 'SKU-7621', 'SKU-4156'],
        'Product': ['Premium Widget', 'Smart Connector', 'Eco Package', 'Pro Adapter', 'Standard Kit'],
        'Current Stock': [85, 42, 156, 28, 93],
        'Daily Demand': [12, 8, 18, 5, 15],
        'Days Until Stockout': [7, 5, 9, 6, 6],
        'Reorder Point': [120, 95, 200, 80, 140],
        'Status': ['WARNING', 'CRITICAL', 'OK', 'WARNING', 'WARNING']
    })
    
    st.dataframe(risk_data, use_container_width=True, hide_index=True)
    
    st.markdown("""<div style='background:#DC2626;border-radius:8px;padding:12px 16px;margin-top:12px;color:#FEE2E2;font-size:14px;'><b>Action Required:</b> Initiate emergency purchase orders for SKU-5847 and SKU-7621 immediately</div>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    
    # ABC Classification
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:20px;font-weight:600;'>ABC Inventory Classification</h3></div>""", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        abc_stats = pd.DataFrame({
            'Category': ['A-Items', 'B-Items', 'C-Items'],
            'SKU Count': [186, 434, 620],
            '% of SKUs': ['15%', '35%', '50%'],
            'Revenue %': ['80%', '15%', '5%'],
            'Control Level': ['Tight', 'Medium', 'Loose']
        })
        st.dataframe(abc_stats, use_container_width=True, hide_index=True)
    
    with col_right:
        abc_values = [80, 15, 5]
        abc_labels = ['A-Items (15% SKUs)', 'B-Items (35% SKUs)', 'C-Items (50% SKUs)']
        fig_abc = go.Figure(data=[go.Pie(
            labels=abc_labels, values=abc_values,
            marker=dict(colors=['#3B82F6', '#06B6D4', '#8B5CF6'])
        )])
        fig_abc.update_layout(height=300, template='plotly_dark')
        st.plotly_chart(fig_abc, use_container_width=True)
    
    st.markdown("""<div style='margin:24px 0 16px 0;'><p style='color:#6B7280;font-size:14px;'><b>A-Items (High Priority):</b> Daily monitoring, 2-week reorder cycle | <b>B-Items:</b> Weekly reviews, 4-week reorder | <b>C-Items:</b> Monthly reviews, 8-week reorder</p></div>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    
    # Top Performers
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:20px;font-weight:600;'>Fast-Moving SKUs (Top 10)</h3></div>""", unsafe_allow_html=True)
    
    fast_moving = pd.DataFrame({
        'SKU': ['SKU-3045', 'SKU-1098', 'SKU-5432', 'SKU-2187', 'SKU-9876', 'SKU-4321', 'SKU-6789', 'SKU-2109', 'SKU-8765', 'SKU-5678'],
        'Product': ['Premium Widget', 'Smart Connector', 'Eco Package', 'Pro Adapter', 'Standard Kit', 'Basic Accessory', 'Pro Bundle', 'Eco Starter', 'Premium Plus', 'Value Pack'],
        'Monthly Sales': [8500, 7200, 6800, 5900, 5400, 4800, 4200, 3900, 3600, 3100],
        'Turnover Rate': ['18.2x', '16.4x', '15.8x', '14.2x', '13.5x', '12.1x', '11.8x', '10.9x', '9.8x', '9.1x'],
        'Days Inventory': [20, 22, 23, 26, 27, 30, 31, 33, 37, 40]
    })
    
    fig_fast = px.bar(
        fast_moving.head(10), x='Monthly Sales', y='SKU', orientation='h',
        color='Turnover Rate', color_continuous_scale='Greens',
        title='Top 10 Fast-Moving SKUs'
    )
    fig_fast.update_layout(height=350, template='plotly_dark')
    st.plotly_chart(fig_fast, use_container_width=True)
    
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    
    # Slow-Moving & Liquidation
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:20px;font-weight:600;'>Slow-Moving Inventory for Liquidation</h3></div>""", unsafe_allow_html=True)
    
    slow_moving = pd.DataFrame({
        'SKU': ['SKU-0001', 'SKU-0002', 'SKU-0003', 'SKU-0004', 'SKU-0005'],
        'Product': ['Legacy Model A', 'Discontinued B', 'Old Version C', 'Obsolete D', 'Superseded E'],
        'Current Stock': [340, 215, 128, 89, 156],
        'Value Tied Up': ['$8,500', '$5,375', '$3,200', '$2,225', '$3,900'],
        'Days Since Sale': [287, 263, 198, 154, 312],
        'Recommendation': ['Liquidate 50%', 'Liquidate 75%', 'Clearance Sale', 'Donate/Recycle', 'Deep Discount']
    })
    
    st.dataframe(slow_moving, use_container_width=True, hide_index=True)
    
    st.markdown("""<div style='background:#10B981;border-radius:8px;padding:12px 16px;margin-top:12px;color:#ECFDF5;font-size:14px;'><b>Savings Opportunity:</b> Liquidating this inventory could free up $23,200 in carrying costs and improve cash flow</div>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    
    # Optimization Recommendations
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:20px;font-weight:600;'>Optimization Recommendations</h3></div>""", unsafe_allow_html=True)
    
    recommendations = pd.DataFrame({
        'Priority': ['High', 'High', 'Medium', 'Medium'],
        'Recommendation': [
            'Adjust reorder points for A-items',
            'Liquidate slow-moving inventory',
            'Implement cycle counting program',
            'Evaluate supplier lead times'
        ],
        'Expected Savings': ['$28,500/year', '$23,200 one-time', '$8,400/year', '$12,100/year'],
        'Implementation': ['2-3 weeks', '4-6 weeks', '8 weeks', '6 weeks']
    })
    
    st.dataframe(recommendations, use_container_width=True, hide_index=True)
