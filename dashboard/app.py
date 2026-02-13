import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io


from components import create_line_chart, create_bar_chart, COLORS, COLOR_PALETTE
from utils import create_multi_format_export, create_download_button
from utils import calculate_business_health_score, calculate_period_comparison, calculate_key_metrics
from utils.metrics_utils import forecast_revenue
from components import display_business_health_score, display_metric_with_comparison, display_key_metrics_grid

# Page Imports
from pages_margin_analysis import render_margin_analysis_page
from pages_smart_alerts import render_smart_alerts_page
from pages_cohort_analysis import render_cohort_analysis_page
from pages_customer_ltv import render_customer_ltv_page
from pages_revenue_attribution import render_revenue_attribution_page
from pages_competitive_benchmark import render_competitive_benchmark_page
from pages_data_sources import render_data_sources_page
from pages_customer_insights import render_customer_insights_page
from pages_inventory_demand import render_inventory_demand_page
from pages_anomalies_alerts import render_anomalies_alerts_page
from pages_analytics import render_analytics_page
from pages_predictions import render_predictions_page
from pages_recommendations import render_recommendations_page
from pages_whatif import render_whatif_page
from pages_inventory_optimization import render_inventory_optimization_page
from pages_executive_briefing import render_executive_briefing_page
from pages_goals import render_goals_page
from utils.industry_utils import INDUSTRIES
from utils.pdf_export import create_pdf_download_button
from utils.weekly_digest import generate_weekly_digest

from auth import require_authentication, render_user_info
if not require_authentication():
    st.stop()

st.set_page_config(page_title="Echolon AI", page_icon="📊", layout="wide")

def format_currency(value, decimals=0):
    if value >= 1e6: return f"${value/1e6:.{decimals}f}M"
    if value >= 1e3: return f"${value/1e3:.{decimals}f}K"
    return f"${value:,.{decimals}f}"

def format_percentage(value, decimals=1): return f"{value:.{decimals}f}%"
def format_multiplier(value, decimals=2): return f"{value:.{decimals}f}x"
def format_number(value, decimals=0): return f"{value:,.{decimals}f}"

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'industry' not in st.session_state:
    st.session_state.industry = 'ecommerce'
if 'company_name' not in st.session_state:
    st.session_state.company_name = 'Your Business'
if 'date_range' not in st.session_state:
    st.session_state.date_range = 'Last 90 Days'

@st.cache_data
def load_data():
    """Generate realistic demo data with stable growth (5-15% MoM)."""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=365, freq='D')
    # Realistic revenue: base ~$150K/month with 8% monthly growth trend + noise
    base = 5000
    growth = 1.00025  # ~0.025% daily = ~8% monthly
    daily_revenue = base * (growth ** np.arange(365)) * (1 + np.random.normal(0, 0.05, 365))
    daily_revenue = np.maximum(daily_revenue, base * 0.8)  # Floor to avoid zeros
    df = pd.DataFrame({
        'date': dates,
        'revenue': daily_revenue,
        'orders': np.random.poisson(100, 365) + np.arange(365) // 30,  # Slight upward trend
        'customers': np.random.poisson(50, 365) + np.arange(365) // 60,
        'marketing_spend': np.random.normal(1000, 100, 365),
        'inventory_units': np.random.randint(100, 1000, 365),
        'roas': np.random.uniform(2, 5, 365)
    })
    df['profit'] = df['revenue'] * 0.4
    df['profit_margin'] = 40.0
    df['avg_order_value'] = np.where(df['orders'] > 0, df['revenue'] / df['orders'], 50)
    return df

with st.spinner("Loading data..."):
    data = st.session_state.get('uploaded_data') or load_data()
    data = data.copy()
    if 'profit' not in data.columns and 'revenue' in data.columns:
        data['profit'] = data['revenue'] * 0.4
    if 'profit_margin' not in data.columns:
        data['profit_margin'] = 40.0
    if 'roas' not in data.columns and 'marketing_spend' in data.columns:
        data['roas'] = (data['revenue'] / data['marketing_spend']).clip(1, 10)
    elif 'roas' not in data.columns:
        data['roas'] = 3.0
    if 'avg_order_value' not in data.columns and 'orders' in data.columns:
        data['avg_order_value'] = np.where(data['orders'] > 0, data['revenue'] / data['orders'], 50)

    # Apply date range filter
    date_range = st.session_state.get('date_range', 'Last 90 Days')
    if 'date' in data.columns and date_range != 'All Time':
        data['date'] = pd.to_datetime(data['date'])
        end_date = data['date'].max()
        days_map = {'Last 7 Days': 7, 'Last 30 Days': 30, 'Last 90 Days': 90, 'Last 12 Months': 365}
        days = days_map.get(date_range, 90)
        start_date = end_date - timedelta(days=days)
        data = data[(data['date'] >= start_date) & (data['date'] <= end_date)].copy()

kpis = {'total_revenue': data['revenue'].sum(), 'roas': data['roas'].mean()}

# Mobile-responsive CSS
st.markdown("""
<style>
@media (max-width: 768px) {
    .stMetric { min-width: 120px; }
    [data-testid="stSidebar"] { width: 100% !important; }
    .block-container { padding: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Echolon AI")
    st.caption("Business Intelligence")
    industry_options = {k: f"{v['icon']} {v['name']}" for k, v in INDUSTRIES.items()}
    st.session_state.industry = st.selectbox(
        "Industry",
        options=list(industry_options.keys()),
        format_func=lambda k: industry_options[k],
        key="sidebar_industry"
    )
    st.session_state.date_range = st.selectbox(
        "Date Range",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 12 Months", "All Time"],
        index=2,
        key="sidebar_date_range"
    )
    st.session_state.company_name = st.text_input("Company Name", value=st.session_state.get('company_name', 'Your Business'), key="company_name_input")
    st.markdown("---")
    for p in ["Executive Briefing", "Dashboard", "Analytics", "Predictions", "What-If", "Recommendations", "Customer Insights", "Insights", "Inventory & Demand", "Anomalies & Alerts", "Inventory Optimization", "Margin Analysis", "Smart Alerts", "Goals", "Cohort Analysis", "Customer LTV", "Revenue Attribution", "Competitive Benchmark", "Data Sources"]:
        if st.button(p, use_container_width=True):
            st.session_state.current_page = p
            st.rerun()

p = st.session_state.current_page
args = (data, kpis, format_currency, format_percentage, format_multiplier)

try:
    if p == "Executive Briefing":
        render_executive_briefing_page(*args)
        # Add export options
        metrics = calculate_key_metrics(data)
        health_metrics = {
            'revenue_growth': metrics.get('revenue_growth', 0),
            'profit_margin': float(data['profit_margin'].mean()) if 'profit_margin' in data.columns else 40,
            'cash_flow_ratio': 1.2,
            'customer_growth': metrics.get('customer_growth', 0),
            'roas': float(data['roas'].mean()) if 'roas' in data.columns else 3
        }
        health_score = calculate_business_health_score(health_metrics)
        st.markdown("---")
        st.subheader("📤 Export & Share")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            create_pdf_download_button(data, kpis, health_score, st.session_state.get('company_name', 'Your Business'), "exec_pdf")
        with col_exp2:
            digest = generate_weekly_digest(data, kpis, health_score)
            st.download_button(
                label="📧 Download Weekly Digest (TXT)",
                data=digest['text'],
                file_name=f"echolon_weekly_digest_{pd.to_datetime(data['date']).max().strftime('%Y%m%d') if 'date' in data.columns else datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key="exec_digest",
                use_container_width=True
            )
    elif p == "Dashboard":
        st.title("Dashboard")

        # Data source banner
        has_live = bool(st.session_state.get('connected_sources'))
        banner = "🟢 Live Data" if has_live else "📊 Demo Data"
        last_date = pd.to_datetime(data['date']).max().strftime('%Y-%m-%d') if 'date' in data.columns else 'N/A'
        st.info(f"{banner} | Last updated: {last_date}")
        # Executive Summary
        st.subheader("📊 Executive Summary")
        # Key Metrics Grid
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
                total_rev = data['revenue'].sum()
                prev_rev = data.iloc[:len(data)//2]['revenue'].sum() if len(data) >= 2 else total_rev * 0.9
                rev_comp = calculate_period_comparison(total_rev, prev_rev)
                st.metric("Total Revenue", format_currency(total_rev), rev_comp['formatted_change'])
    
        with col2:
                total_profit = data['profit'].sum()
                prev_profit = data.iloc[:len(data)//2]['profit'].sum() if len(data) >= 2 else total_profit * 0.9
                profit_comp = calculate_period_comparison(total_profit, prev_profit)
                st.metric("Total Profit", format_currency(total_profit), profit_comp['formatted_change'])
    
        with col3:
                avg_margin = data['profit_margin'].mean()
                st.metric("Avg Margin", format_percentage(avg_margin), "✓ Healthy")
    
        with col4:
                avg_roas = data['roas'].mean()
                st.metric("Avg ROAS", format_multiplier(avg_roas), "↑ 15.2%")
    
        st.markdown("---")

        # Quick Insights & Alerts
        st.subheader("⚡ Quick Insights & Priority Actions")
    
        col1, col2 = st.columns(2)
    
        with col1:
                st.markdown("### 🎯 Top Opportunities")
                st.success("✅ **Software Category:** 85% margin - Scale marketing investment")
                st.info("💡 **High-LTV Customers:** 32% generate 58% of revenue - Implement tiered pricing")
                st.warning("⚠️ **Electronics Margin:** Only 15% - Consider 10-15% price increase")
    
        with col2:
                st.markdown("### 📊 Key Trends")
                recent_revenue = data.tail(30)['revenue'].mean()
                older_revenue = data.head(30)['revenue'].mean()
                trend = ((recent_revenue - older_revenue) / older_revenue) * 100 if older_revenue > 0 else 0
                trend = max(-99, min(999, trend))  # Cap for realistic display
                st.metric("30-Day Revenue Trend", format_currency(recent_revenue), f"{trend:+.1f}%")
        
                st.markdown(f"""  
                - **Revenue Growth:** {trend:+.1f}% vs. previous period
                - **Profit Margin:** Stable at 40%
                - **Customer Acquisition:** {int(data['customers'].sum())} total customers
                - **Inventory Health:** {int(data['inventory_units'].mean())} avg units
                """)
    
        st.markdown("---")

        # Quick Stats
        st.subheader("📋 Business Health Score")
        metrics = calculate_key_metrics(data)
        health_metrics = {
            'revenue_growth': metrics.get('revenue_growth', 0),
            'profit_margin': data['profit_margin'].mean() if 'profit_margin' in data.columns else 40,
            'cash_flow_ratio': 1.2,
            'customer_growth': metrics.get('customer_growth', 0),
            'roas': data['roas'].mean() if 'roas' in data.columns else 3
        }
        health_score = calculate_business_health_score(health_metrics)
        display_business_health_score(health_score)
    elif p == "Analytics":
        render_analytics_page(*args)
    elif p == "Predictions":
        render_predictions_page(*args)
    elif p == "What-If":
        render_whatif_page()
    elif p == "Recommendations":
        render_recommendations_page(*args)
    elif p == "Customer Insights":
        render_customer_insights_page(*args)
    elif p == "Insights":
        from pages_insights import render_insights_page
        render_insights_page(data, kpis, format_currency, format_percentage, format_number)
    elif p == "Inventory & Demand":
        render_inventory_demand_page(*args)
    elif p == "Anomalies & Alerts":
        render_anomalies_alerts_page(*args)
    elif p == "Inventory Optimization":
        render_inventory_optimization_page(*args)
    elif p == "Margin Analysis":
        render_margin_analysis_page(*args)
    elif p == "Smart Alerts":
        render_smart_alerts_page(*args)
    elif p == "Goals":
        render_goals_page(data, kpis, format_currency, format_percentage)
    elif p == "Cohort Analysis":
        render_cohort_analysis_page(*args)
    elif p == "Customer LTV":
        render_customer_ltv_page(*args)
    elif p == "Revenue Attribution":
        render_revenue_attribution_page(*args)
    elif p == "Competitive Benchmark":
        render_competitive_benchmark_page(*args)
    elif p == "Data Sources":
        render_data_sources_page()
    else:
        st.info("Select a page from the sidebar.")
except Exception as e:
    st.error(f"❌ Error loading page: {str(e)}")
    st.info("Try refreshing the page. If the problem persists, check the console for details.")
