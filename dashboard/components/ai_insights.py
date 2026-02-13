"""AI-Powered Insights and Analytics Enhancements for Echolon AI Dashboard"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

def generate_ai_insights(data, kpis=None):
    """
    Generate AI-powered insights from business data.
    Uses personalized_insights engine for real, actionable feedback.
    """
    try:
        from utils import calculate_key_metrics, generate_personalized_insights
        metrics = calculate_key_metrics(data) if data is not None else {}
        if kpis:
            metrics.update(kpis)
        return generate_personalized_insights(data, metrics)
    except Exception:
        pass
    
    # Fallback if personalized_insights unavailable
    insights = []
    if data is None or data.empty:
        return insights
    
    # Revenue trend analysis
    if 'revenue' in data.columns:
        revenue_trend = (kpis or {}).get('revenue_growth', 0)
        if revenue_trend > 5:
            insights.append({
                'type': 'positive',
                'icon': '📈',
                'title': 'Strong Revenue Growth',
                'message': f"Revenue increased by {revenue_trend:.1f}% compared to the previous period.",
                'action': 'Consider increasing marketing spend to capitalize on this momentum.'
            })
        elif revenue_trend < -5:
            insights.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'Revenue Decline Detected',
                'message': f"Revenue decreased by {abs(revenue_trend):.1f}% compared to the previous period.",
                'action': 'Review marketing campaigns and consider customer retention strategies.'
            })
    
    # Customer analysis
    if 'customers' in data.columns:
        recent_customers = data.tail(7)['customers'].mean()
        previous_customers = data.iloc[-14:-7]['customers'].mean() if len(data) >= 14 else recent_customers
        
        if recent_customers > previous_customers * 1.1:
            insights.append({
                'type': 'positive',
                'icon': '🎯',
                'title': 'Customer Acquisition Accelerating',
                'message': f"Daily customer count increased by {((recent_customers/previous_customers - 1) * 100):.1f}% in the last week.",
                'action': 'Analyze which channels are driving this growth and double down on them.'
            })
    
    # Order value analysis
    if 'revenue' in data.columns and 'orders' in data.columns:
        avg_order_value = (kpis or {}).get('avg_order_value', data['revenue'].sum() / data['orders'].sum() if data['orders'].sum() > 0 else 0)
        if avg_order_value > 0:
            insights.append({
                'type': 'info',
                'icon': '💰',
                'title': 'Average Order Value',
                'message': f"Current average order value is ${avg_order_value:.2f}.",
                'action': 'Consider upselling and cross-selling strategies to increase order value.'
            })
    
    # Profit margin analysis
    if 'profit_margin' in data.columns:
        avg_margin = (kpis or {}).get('avg_profit_margin', data['profit_margin'].mean())
        if avg_margin > 30:
            insights.append({
                'type': 'positive',
                'icon': '✨',
                'title': 'Healthy Profit Margins',
                'message': f"Average profit margin of {avg_margin:.1f}% indicates strong business fundamentals.",
                'action': 'Maintain current pricing strategy and focus on scaling.'
            })
        elif avg_margin < 15:
            insights.append({
                'type': 'warning',
                'icon': '📉',
                'title': 'Low Profit Margins',
                'message': f"Profit margin of {avg_margin:.1f}% may be unsustainable long-term.",
                'action': 'Review cost structure and consider price optimization.'
            })
    
    # Peak performance day
    if 'revenue' in data.columns and 'date' in data.columns:
        best_day = data.loc[data['revenue'].idxmax()]
        insights.append({
            'type': 'info',
            'icon': '🏆',
            'title': 'Best Performing Day',
            'message': f"Highest revenue of ${best_day['revenue']:.2f} occurred on {pd.to_datetime(best_day['date']).strftime('%B %d, %Y')}.",
            'action': 'Analyze what made this day successful and replicate those conditions.'
            })
    
    return insights

def display_insights_panel(insights):
    """
    Display AI insights in an attractive panel format.
    Supports personalized insights with impact field.
    """
    st.markdown("### 💡 AI-Powered Insights")
    
    if not insights:
        st.info("Analyzing your data to generate insights...")
        return
    
    for insight in insights:
        # Choose color based on insight type
        itype = insight.get('type', 'info')
        if itype == 'positive':
            border_color = "#28a745"
        elif itype in ('warning', 'critical'):
            border_color = "#ffc107" if itype == 'warning' else "#dc3545"
        elif itype == 'opportunity':
            border_color = "#17a2b8"
        else:
            border_color = "#17a2b8"
        
        impact_line = f"<p style='margin: 4px 0 0 0; color: #6c757d; font-size: 12px;'>{insight.get('impact', '')}</p>" if insight.get('impact') else ""
        
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {border_color};
                padding: 15px;
                margin: 10px 0;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            ">
                <h4 style="margin: 0 0 10px 0;">{insight.get('icon', '💡')} {insight['title']}</h4>
                <p style="margin: 5px 0; color: #ddd;">{insight['message']}</p>
                <p style="margin: 5px 0; color: #aaa; font-style: italic;">💼 Recommended Action: {insight['action']}</p>
                {impact_line}
            </div>
            """,
            unsafe_allow_html=True
        )

def export_data_to_csv(data):
    """
    Export dataframe to CSV format for download
    """
    if data is None or data.empty:
        return None
    
    # Convert to CSV
    csv = data.to_csv(index=False)
    return csv

def create_date_filter():
    """
    Create date range filter widget
    Returns: (start_date, end_date)
    """
    st.sidebar.markdown("### 📅 Date Range Filter")
    
    # Preset options
    date_options = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Year to Date": None,
        "Custom Range": "custom"
    }
    
    selected_range = st.sidebar.selectbox(
        "Select Time Period",
        list(date_options.keys()),
        index=1  # Default to Last 30 Days
    )
    
    if selected_range == "Custom Range":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
    elif selected_range == "Year to Date":
        start_date = datetime(datetime.now().year, 1, 1)
        end_date = datetime.now()
    else:
        days = date_options[selected_range]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
    
    return start_date, end_date

def filter_data_by_date(data, start_date, end_date):
    """
    Filter dataframe by date range
    """
    if data is None or data.empty or 'date' not in data.columns:
        return data
    
    # Ensure date column is datetime
    data['date'] = pd.to_datetime(data['date'])
    
    # Convert start_date and end_date to datetime if they aren't already
    if not isinstance(start_date, pd.Timestamp):
        start_date = pd.to_datetime(start_date)
    if not isinstance(end_date, pd.Timestamp):
        end_date = pd.to_datetime(end_date)
    
    # Filter
    filtered_data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
    
    return filtered_data

def create_comparison_metrics(data, metric_name):
    """
    Calculate period-over-period comparison metrics
    Returns: (current_value, previous_value, percent_change)
    """
    if data is None or data.empty or metric_name not in data.columns:
        return None, None, None
    
    # Split data into two equal periods
    mid_point = len(data) // 2
    
    if mid_point == 0:
        return None, None, None
    
    current_period = data.iloc[mid_point:]
    previous_period = data.iloc[:mid_point]
    
    current_value = current_period[metric_name].sum()
    previous_value = previous_period[metric_name].sum()
    
    if previous_value > 0:
        percent_change = ((current_value - previous_value) / previous_value) * 100
    else:
        percent_change = 0
    
    return current_value, previous_value, percent_change

def display_export_button(data, filename="echolon_export.csv"):
    """
    Display a download button for exporting data
    """
    if data is None or data.empty:
        return
    
    csv = export_data_to_csv(data)
    
    st.download_button(
        label="📥 Export Data to CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        help="Download your data as a CSV file"
    )

def calculate_advanced_kpis(data):
    """
    Calculate advanced business KPIs
    Returns: dict of advanced metrics
    """
    if data is None or data.empty:
        return {}
    
    advanced_kpis = {}
    
    # Customer Lifetime Value (simplified)
    if 'revenue' in data.columns and 'customers' in data.columns:
        total_revenue = data['revenue'].sum()
        total_customers = data['customers'].sum()
        if total_customers > 0:
            advanced_kpis['customer_lifetime_value'] = total_revenue / total_customers
    
    # Revenue per order
    if 'revenue' in data.columns and 'orders' in data.columns:
        total_revenue = data['revenue'].sum()
        total_orders = data['orders'].sum()
        if total_orders > 0:
            advanced_kpis['revenue_per_order'] = total_revenue / total_orders
    
    # Conversion rate (customers / orders)
    if 'customers' in data.columns and 'orders' in data.columns:
        total_customers = data['customers'].sum()
        total_orders = data['orders'].sum()
        if total_orders > 0:
            advanced_kpis['conversion_rate'] = (total_customers / total_orders) * 100
    
    # Daily average metrics
    for col in ['revenue', 'orders', 'customers']:
        if col in data.columns:
            advanced_kpis[f'daily_avg_{col}'] = data[col].mean()
    
    return advanced_kpis
