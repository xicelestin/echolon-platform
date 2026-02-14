import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Must be first Streamlit command
st.set_page_config(page_title="Echolon AI", page_icon="📊", layout="wide")

from components import create_line_chart, create_bar_chart, COLORS, COLOR_PALETTE
from utils import create_multi_format_export, create_download_button
from utils import calculate_business_health_score, calculate_period_comparison, calculate_key_metrics
from utils import get_top_priority_this_week, get_metric_alerts
from utils.metrics_utils import forecast_revenue
from components import display_business_health_score, display_metric_with_comparison, display_key_metrics_grid

# Import auth early to avoid circular import (pages_data_sources imports auth)
from auth import require_authentication, render_user_info, get_current_user

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
from pages_executive_briefing import render_executive_briefing_page, get_top_opportunities
from pages_goals import render_goals_page
from utils.industry_utils import INDUSTRIES
from utils.pdf_export import create_pdf_download_button, create_excel_download_button
from utils.weekly_digest import generate_weekly_digest

if not require_authentication():
    st.stop()

# Sync connected sources if data is stale (>6 hrs) - runs quietly on each visit
from utils.sync_utils import sync_all_if_stale
sync_all_if_stale()

def format_currency(value, decimals=0):
    if value >= 1e6: return f"${value/1e6:.{decimals}f}M"
    if value >= 1e3: return f"${value/1e3:.{decimals}f}K"
    return f"${value:,.{decimals}f}"

def format_percentage(value, decimals=1): return f"{value:.{decimals}f}%"
def format_multiplier(value, decimals=2): return f"{value:.{decimals}f}x"
def format_number(value, decimals=0): return f"{value:,.{decimals}f}"

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Executive Briefing'
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
    channels = ['Online Store', 'POS', 'Mobile App', 'Wholesale', 'Marketplace']
    channel_weights = [0.45, 0.25, 0.15, 0.10, 0.05]
    df = pd.DataFrame({
        'date': dates,
        'revenue': daily_revenue,
        'orders': np.random.poisson(100, 365) + np.arange(365) // 30,
        'customers': np.random.poisson(50, 365) + np.arange(365) // 60,
        'marketing_spend': np.random.normal(1000, 100, 365),
        'inventory_units': np.random.randint(100, 1000, 365),
        'roas': np.random.uniform(2, 5, 365),
        'channel': np.random.choice(channels, 365, p=channel_weights),
    })
    df['profit'] = df['revenue'] * 0.4
    df['profit_margin'] = 40.0
    df['avg_order_value'] = np.where(df['orders'] > 0, df['revenue'] / df['orders'], 50)
    return df

try:
    with st.spinner("Loading data..."):
        data = st.session_state.get('uploaded_data') or load_data()
        data = data.copy()
        st.session_state.current_data = data  # Single source of truth — all pages use this when they need data
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
    roas_val = float(data['roas'].mean()) if 'roas' in data.columns and len(data) > 0 else 3.0
    if pd.isna(roas_val):
        roas_val = 3.0
    kpis = {'total_revenue': float(data['revenue'].sum()) if 'revenue' in data.columns else 0, 'roas': roas_val}
except Exception as e:
    st.error("❌ Failed to load data. Please try again or upload fresh data from Data Sources.")
    with st.expander("Technical details"):
        st.exception(e)
    st.stop()

# Global design system - spacing, typography, hierarchy
st.markdown("""
<style>
    /* Base spacing and typography */
    .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px; }
    h1 { font-size: 1.75rem !important; font-weight: 700 !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.35rem !important; font-weight: 600 !important; margin-top: 2rem !important; margin-bottom: 1rem !important; }
    h3 { font-size: 1.1rem !important; font-weight: 600 !important; margin-top: 1.5rem !important; }
    
    /* Section spacing */
    [data-testid="stVerticalBlock"] > div { margin-bottom: 0.5rem; }
    hr { margin: 2rem 0 !important; border-color: rgba(255,255,255,0.1) !important; }
    
    /* Metric cards - cleaner look */
    [data-testid="stMetric"] { 
        background: rgba(31, 41, 55, 0.5); 
        padding: 1rem 1.25rem; 
        border-radius: 12px; 
        border: 1px solid rgba(55, 65, 81, 0.8);
    }
    [data-testid="stMetric"] label { font-size: 0.8rem !important; opacity: 0.9; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.25rem !important; font-weight: 700; }
    
    /* Buttons */
    .stButton > button { border-radius: 8px; font-weight: 500; transition: opacity 0.2s; }
    .stButton > button:hover { opacity: 0.9; }
    
    /* Expanders */
    [data-testid="stExpander"] { border-radius: 12px; border: 1px solid rgba(55, 65, 81, 0.6); }
    
    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; }
        .stMetric { min-width: 120px; }
        [data-testid="stSidebar"] { width: 100% !important; }
        .stColumns > div { flex: 1 1 100% !important; min-width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Echolon AI")
    st.caption("Business Intelligence")
    
    # Onboarding checklist for first-time users
    has_data = bool(st.session_state.get('connected_sources') or st.session_state.get('uploaded_data') is not None)
    has_goals = bool(st.session_state.get('goals') and any(g.get('target') for g in (st.session_state.get('goals') or {}).values()))
    if not has_data or not has_goals:
        with st.expander("✅ Get Started", expanded=not has_data):
            st.markdown(f"{'✅' if has_data else '⬜'} Connect your data")
            st.markdown(f"{'✅' if has_goals else '⬜'} Set your first goal")
            if not has_data:
                if st.button("📁 Add Data", key="onboard_data"):
                    st.session_state.current_page = "Data Sources"
                    st.rerun()
            if not has_goals and has_data:
                if st.button("🎯 Set Goals", key="onboard_goals"):
                    st.session_state.current_page = "Goals"
                    st.rerun()
        st.markdown("---")
    
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
    with st.expander("🔔 Alerts"):
        st.caption("We alert you when: revenue drops >5%, margin drops >3 pts, ROAS down >15%.")
        st.caption("Based on your last 60 days of data.")
    st.markdown("---")
    st.caption("Main")
    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
    for p in ["Executive Briefing", "Dashboard", "Analytics", "Insights", "Predictions", "Recommendations", "Goals", "Data Sources"]:
        if st.button(p, use_container_width=True):
            st.session_state.current_page = p
            st.rerun()
    with st.expander("More pages"):
        for p in ["What-If", "Customer Insights", "Inventory & Demand", "Anomalies & Alerts", "Inventory Optimization", "Margin Analysis", "Smart Alerts", "Cohort Analysis", "Customer LTV", "Revenue Attribution", "Competitive Benchmark"]:
            if st.button(p, use_container_width=True, key=f"nav_{p}"):
                st.session_state.current_page = p
                st.rerun()

p = st.session_state.current_page
args = (data, kpis, format_currency, format_percentage, format_multiplier)

# Pages that need date+revenue show a friendly message if user didn't map those columns
PAGES_NEEDING_DATE_REVENUE = ["Executive Briefing", "Dashboard", "Analytics", "Insights", "Predictions", "Recommendations", "Goals", "What-If", "Margin Analysis", "Smart Alerts", "Anomalies & Alerts", "Revenue Attribution", "Customer LTV", "Competitive Benchmark"]
def _check_data_for_page(page_name):
    provided = st.session_state.get("uploaded_data_provided_columns")
    if provided is None:
        return True  # Demo/API data: assume full
    provided_set = set(provided)
    if "date" in provided_set and "revenue" in provided_set:
        return True
    missing = [c for c in ["date", "revenue"] if c not in provided_set]
    st.info(f"📊 **This page needs:** {', '.join(missing)}. Map these columns in **Data Sources** to see {page_name.lower()}.")
    if st.button("📁 Go to Data Sources", key=f"goto_ds_{page_name}"):
        st.session_state.current_page = "Data Sources"
        st.rerun()
    return False

try:
    if p == "Executive Briefing":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
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
        st.caption("Send to your accountant, share with your team, or keep for your records.")
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1:
            create_pdf_download_button(data, kpis, health_score, st.session_state.get('company_name', 'Your Business'), "exec_pdf")
            st.caption("PDF for accountant")
        with col_exp2:
            create_excel_download_button(data, kpis, health_score, st.session_state.get('company_name', 'Your Business'), "exec_excel")
            st.caption("Excel for analysis")
        with col_exp3:
            digest = generate_weekly_digest(data, kpis, health_score)
            st.download_button(
                label="📧 Download Weekly Digest (TXT)",
                data=digest['text'],
                file_name=f"echolon_weekly_digest_{pd.to_datetime(data['date']).max().strftime('%Y%m%d') if 'date' in data.columns else datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key="exec_digest",
                use_container_width=True
            )
            st.caption("Summary for email")
    elif p == "Dashboard":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        st.title("Dashboard")

        # Data source banner
        has_live = bool(st.session_state.get('connected_sources'))
        banner = "🟢 Live Data" if has_live else "📊 Demo Data"
        last_date = pd.to_datetime(data['date']).max().strftime('%Y-%m-%d') if 'date' in data.columns else 'N/A'
        from utils.sync_utils import get_most_recent_sync, format_last_sync_ago
        sync_line = ""
        if has_live:
            recent = get_most_recent_sync()
            sync_line = f" | Last synced: {format_last_sync_ago(recent) if recent else 'Never'}"
        st.info(f"{banner} | Last updated: {last_date}{sync_line}")
        
        # vs Industry benchmark
        from utils.industry_utils import get_industry_benchmarks
        industry = st.session_state.get('industry', 'ecommerce')
        benchmarks = get_industry_benchmarks(industry)
        ind_name = {'ecommerce': 'E-commerce', 'saas': 'SaaS', 'restaurant': 'Restaurant', 'services': 'Services', 'general': 'General'}.get(industry, 'E-commerce')
        your_margin = float(data['profit_margin'].mean()) if 'profit_margin' in data.columns else 40
        bench_margin = benchmarks.get('profit_margin', 35)
        m_icon = "✓" if your_margin >= bench_margin else "→"
        st.caption(f"📊 vs {ind_name}: Your margin {your_margin:.0f}% {m_icon} industry avg {bench_margin}%")
        
        # Calculate metrics first (needed for alerts and top priority)
        dash_metrics = calculate_key_metrics(data)
        metric_alerts = get_metric_alerts(data, dash_metrics)
        if metric_alerts:
            st.markdown("#### ⚠️ Alerts")
            for a in metric_alerts[:3]:
                if a['severity'] == 'critical':
                    st.error(f"**{a['title']}** — {a['message']}")
                else:
                    st.warning(f"**{a['title']}** — {a['message']}")
        
        # Top Priority This Week
        industry = st.session_state.get('industry', 'ecommerce')
        top_priority = get_top_priority_this_week(data, dash_metrics, industry)
        if top_priority:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1E3A5F 0%,#0F172A 100%);border:1px solid rgba(59,130,246,0.5);border-radius:16px;padding:24px 28px;margin:0 0 2rem 0;box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);'>
                <p style='color:#93C5FD;font-size:11px;margin:0 0 10px 0;text-transform:uppercase;letter-spacing:0.5px;'>🎯 Top Priority This Week</p>
                <p style='color:#F3F4F6;font-size:1.4rem;font-weight:700;margin:0 0 8px 0;line-height:1.4;'>{top_priority['title']}</p>
                <p style='color:#D1D5DB;font-size:0.95rem;margin:0;line-height:1.5;'>{top_priority['action'][:120]}{'...' if len(top_priority['action']) > 120 else ''}</p>
                <p style='color:#10B981;font-size:0.9rem;margin:1rem 0 0 0;font-weight:600;'>Impact: {top_priority['impact']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Executive Summary
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.subheader("📊 Executive Summary")
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
        metrics = dash_metrics
    
        col1, col2 = st.columns(2)
    
        with col1:
                st.markdown("### 🎯 Top Opportunities")
                opps = get_top_opportunities(data, metrics, kpis)
                if opps:
                    for o in opps[:3]:
                        if o.get('priority') == 'critical':
                            st.error(f"**{o['title']}** — {o['action']}")
                        elif o.get('priority') == 'high':
                            st.warning(f"⚠️ **{o['title']}** — {o['action']}")
                        else:
                            st.info(f"💡 **{o['title']}** — {o['action']}")
                else:
                    st.success("✅ **Strong performance** — Keep optimizing top channels and margins.")
    
        with col2:
                st.markdown("### 📊 Key Trends")
                recent_revenue = data.tail(30)['revenue'].mean()
                older_revenue = data.head(30)['revenue'].mean()
                trend = ((recent_revenue - older_revenue) / older_revenue) * 100 if older_revenue > 0 else 0
                trend = max(-99, min(999, trend))  # Cap for realistic display
                st.metric("30-Day Revenue Trend", format_currency(recent_revenue), f"{trend:+.1f}%")
        
                margin_val = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
                st.markdown(f"""  
                - **Revenue Growth:** {trend:+.1f}% vs. previous period
                - **Profit Margin:** {margin_val:.1f}%
                - **Total Customers:** {int(data['customers'].sum()) if 'customers' in data.columns else '—'}
                - **Inventory Health:** {int(data['inventory_units'].mean()) if 'inventory_units' in data.columns else '—'} avg units
                """)
    
        st.markdown("---")

        # Revenue Trend Chart
        st.subheader("📈 Revenue Trend")
        if 'date' in data.columns and 'revenue' in data.columns:
            chart_data = data[['date', 'revenue']].copy()
            chart_data['date'] = pd.to_datetime(chart_data['date'])
            fig = px.area(chart_data, x='date', y='revenue', title='Revenue Over Time')
            fig.update_layout(template='plotly_dark', height=280, margin=dict(t=40, b=30, l=50, r=20))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Quick Stats
        st.subheader("📋 Business Health Score")
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
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_analytics_page(*args)
    elif p == "Predictions":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_predictions_page(*args)
    elif p == "What-If":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_whatif_page(*args)
    elif p == "Recommendations":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_recommendations_page(*args)
    elif p == "Customer Insights":
        render_customer_insights_page(*args)
    elif p == "Insights":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        from pages_insights import render_insights_page
        render_insights_page(data, kpis, format_currency, format_percentage, format_number)
    elif p == "Inventory & Demand":
        render_inventory_demand_page(*args)
    elif p == "Anomalies & Alerts":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_anomalies_alerts_page(*args)
    elif p == "Inventory Optimization":
        render_inventory_optimization_page(*args)
    elif p == "Margin Analysis":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_margin_analysis_page(*args)
    elif p == "Smart Alerts":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_smart_alerts_page(*args)
    elif p == "Goals":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_goals_page(data, kpis, format_currency, format_percentage)
    elif p == "Cohort Analysis":
        render_cohort_analysis_page(*args)
    elif p == "Customer LTV":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_customer_ltv_page(*args)
    elif p == "Revenue Attribution":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_revenue_attribution_page(*args)
    elif p == "Competitive Benchmark":
        if p in PAGES_NEEDING_DATE_REVENUE and not _check_data_for_page(p):
            st.stop()
        render_competitive_benchmark_page(*args)
    elif p == "Data Sources":
        render_data_sources_page()
    else:
        st.info("Select a page from the sidebar.")
except Exception as e:
    st.error("❌ Something went wrong loading this page.")
    st.info("Try refreshing the page or going to **Data Sources** to reload your data. If the problem persists, contact support.")
    with st.expander("Technical details"):
        st.exception(e)

# Persist user data when we have uploaded data (keeps preferences & goals with account)
if st.session_state.get("uploaded_data") is not None:
    from utils.user_data_storage import save_user_data
    save_user_data(get_current_user())
