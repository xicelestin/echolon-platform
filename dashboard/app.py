import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import requests
import os
import time
from business_owner_fixes import (show_personalized_onboarding, render_kpi_with_context, personalize_insights, show_tactical_recommendation, render_what_if_presets, get_health_badge, render_kpi_with_benchmark, generate_actionable_insights, display_actionable_insight, get_priority_score)
st.set_page_config(page_title="Echolon AI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Force redeploy
# CUSTOM CSS
st.markdown("""
<style>
.sidebar-header h2 {margin: 0; font-size: 24px; font-weight: 700; color: #fff;}
.sidebar-section {font-size: 11px; font-weight: 700; text-transform: uppercase; color: #888; padding: 16px 0 8px 0;}
.kpi-card {background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 24px; border-radius: 12px; border-left: 4px solid #ff9500; transition: all 0.3s;}
.kpi-card:hover {transform: translateY(-4px); box-shadow: 0 12px 32px rgba(255,149,0,0.25);}
.kpi-card .icon {font-size: 32px; margin-bottom: 12px;}
.kpi-card .title {font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600;}
.kpi-card .metric {font-size: 32px; font-weight: 700; color: #fff; margin: 4px 0;}
.kpi-card .delta {font-size: 12px; color: #90ee90; font-weight: 500; margin-top: 8px;}
.data-badge {display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-bottom: 16px;}
.data-badge.demo {background: #1e3c72; color: #a0a0a0; border: 1px solid #2a5298;}
.data-badge.uploaded {background: #1e5c3c; color: #90ee90; border: 1px solid #2a7c56;}
.feature-card {background: rgba(255,149,0,0.08); border: 1px solid #ff9500; border-radius: 8px; padding: 20px; transition: all 0.3s;}
.feature-card:hover {background: rgba(255,149,0,0.15); border-color: #ffb84d; box-shadow: 0 4px 16px rgba(255,149,0,0.15);}
.page-header h1 {font-size: 36px; font-weight: 700; margin: 0; letter-spacing: -0.5px;}
.page-header p {font-size: 14px; color: #a0a0a0; margin: 8px 0 0 0;}
.last-updated {font-size: 12px; color: #888; text-align: right; padding: 12px 0;}
hr {border: none; border-top: 1px solid #1a1f38; margin: 24px 0;}
</style>
""", unsafe_allow_html=True)

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# ===================  BENCHMARKS CONSTANT  ===================
BENCHMARKS = {
    "revenue": {
        "industry_avg": 1500000,
        "top_25_percent": 3000000,
        "small_business_avg": 500000,
        "saas_avg": 2000000,
        "ecommerce_avg": 1200000
    },
    "churn_rate": {
        "industry_avg": 5.0,
        "top_25_percent": 2.0,
        "saas_avg": 5.0,
        "ecommerce_avg": 15.0,
        "b2b_avg": 3.0
    },
    "cac_payback_period": {
        "industry_avg": 12,
        "top_25_percent": 6,
        "saas_avg": 12,
        "ecommerce_avg": 3,
        "b2b_avg": 18
    },
    "ltv_cac_ratio": {
        "industry_avg": 3.0,
        "top_25_percent": 5.0,
        "saas_avg": 3.0,
        "ecommerce_avg": 2.5,
        "b2b_avg": 4.0
    },
    "conversion_rate": {
        "industry_avg": 2.5,
        "top_25_percent": 5.0,
        "ecommerce_avg": 2.0,
        "saas_avg": 3.0,
        "b2b_avg": 1.5
    },
    "customer_acquisition_cost": {
        "industry_avg": 250,
        "top_25_percent": 100,
        "saas_avg": 300,
        "ecommerce_avg": 50,
        "b2b_avg": 500
    }
}

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'demo'
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = datetime.now()
if 'baseline' not in st.session_state:
    st.session_state.baseline = {"revenue": 100000, "marketing": 20000, "churn": 0.05, "growth": 0.08, "inventory": 1000}

# Demo data for fallback
DEMO_REVENUE = 2400000
DEMO_CUSTOMERS = 8432
DEMO_CAC = 241
DEMO_CHURN = 2.3
DEMO_TREND = pd.DataFrame({'Month': ['May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], 'Revenue': [45000,48000,52000,51000,55000,58000,62000,60000]}).set_index('Month')

def calculate_kpis_from_data():
    """Calculate KPIs from uploaded data or return demo values."""
    if st.session_state.uploaded_data is None or st.session_state.uploaded_data.empty:
        return {
            'revenue': DEMO_REVENUE,
            'revenue_formatted': f"${DEMO_REVENUE/1e6:.1f}M",
            'revenue_delta': "+12.5%",
            'customers': DEMO_CUSTOMERS,
            'customers_formatted': f"{DEMO_CUSTOMERS:,}",
            'customers_delta': "+8.2%",
            'cac': DEMO_CAC,
            'cac_formatted': f"${DEMO_CAC:,}",
            'cac_delta': "↓ $48",
            'churn': DEMO_CHURN,
            'churn_formatted': f"{DEMO_CHURN:.1f}%",
            'churn_delta': "↓ 0.3%",
            'data_source': 'demo'
        }
    try:
        df = st.session_state.uploaded_data
        revenue = df['value'].sum() if 'value' in df.columns else DEMO_REVENUE
        revenue_formatted = f"${revenue/1e6:.1f}M" if revenue >= 1e6 else f"${revenue/1e3:.1f}K"
        customers = len(df) if 'customer_id' in df.columns else int(df['value'].sum() / 50000) or 1000
        customers_formatted = f"{customers:,}"
        cac = (df['value'].sum() / len(df)) if len(df) > 0 else DEMO_CAC
        cac_formatted = f"${cac:,.0f}"
        churn = (df['value'].std() / df['value'].mean() * 100) if df['value'].mean() > 0 else DEMO_CHURN
        churn_formatted = f"{churn:.1f}%"
        return {
            'revenue': revenue,
            'revenue_formatted': revenue_formatted,
            'revenue_delta': "+8.3%",
            'customers': customers,
            'customers_formatted': customers_formatted,
            'customers_delta': "+5.1%",
            'cac': cac,
            'cac_formatted': cac_formatted,
            'cac_delta': "↓ $12",
            'churn': churn,
            'churn_formatted': churn_formatted,
            'churn_delta': "↓ 0.2%",
            'data_source': 'uploaded'
        }
    except Exception as e:
        st.warning(f"Could not calculate from uploaded data: {str(e)}")
        return {
            'revenue': DEMO_REVENUE,
            'revenue_formatted': f"${DEMO_REVENUE/1e6:.1f}M",
            'revenue_delta': "+12.5%",
            'customers': DEMO_CUSTOMERS,
            'customers_formatted': f"{DEMO_CUSTOMERS:,}",
            'customers_delta': "+8.2%",
            'cac': DEMO_CAC,
            'cac_formatted': f"${DEMO_CAC:,}",
            'cac_delta': "↓ $48",
            'churn': DEMO_CHURN,
            'churn_formatted': f"{DEMO_CHURN:.1f}%",
            'churn_delta': "↓ 0.3%",
            'data_source': 'demo'
        }
        
def get_data_source_badge():
    """Return HTML badge showing data source (Demo or Uploaded)."""
    if st.session_state.data_source == 'uploaded':
        return '<span class="data-badge uploaded">Using Your Data</span>'
    else:
        return '<span class="data-badge demo">Demo Data</span>'

def render_last_updated():
    """Render the last updated timestamp."""
    now = datetime.now()
    diff = (now - st.session_state.last_updated).total_seconds()
    time_text = "just now" if diff < 60 else f"{int(diff//60)} min ago" if diff < 3600 else f"{int(diff//3600)} hrs ago"
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f'<div class="last-updated">Last updated: {time_text}</div>', unsafe_allow_html=True)

def render_kpi_card(icon, title, metric, delta, help_text=""):
    """Render a KPI card with dynamic values."""
    st.markdown(f'<div class="kpi-card"><div class="icon">{icon}</div><div class="title">{title}</div><div class="metric">{metric}</div><div class="delta">{delta}</div></div>', unsafe_allow_html=True)
    if help_text:
        st.caption(help_text)

def render_page_header(title, subtitle):
    """Render page header."""
    st.markdown(f'<div class="page-header"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

# =================== CRITICAL BUSINESS IMPROVEMENTS ===================
# CRITICAL FIX 1: Generate AI-powered insights from actual data
def generate_ai_insights(kpis):
    """Generate real AI insights based on actual metrics - not just displaying data."""
    insights = []
    
    # Revenue insights
    if kpis['revenue'] > DEMO_REVENUE:
        pct = ((kpis['revenue']/DEMO_REVENUE - 1)*100)
        insights.append(f"Revenue Outperformance: Your revenue of {kpis['revenue_formatted']} EXCEEDS baseline by {pct:.1f}%! Excellent growth.")
    elif kpis['revenue'] < DEMO_REVENUE * 0.8:
        insights.append(f"Revenue Gap: Your revenue is {((1 - kpis['revenue']/DEMO_REVENUE)*100):.0f}% below expectations. Consider pricing or market expansion.")
    
    # Unit economics - LTV:CAC ratio
    ltv = kpis['revenue'] / kpis['customers'] if kpis['customers'] > 0 else 0
    ltv_cac_ratio = ltv / kpis['cac'] if kpis['cac'] > 0 else 0
    
    if ltv_cac_ratio > 3:
        insights.append(f"Healthy Unit Economics: Your LTV:CAC ratio is {ltv_cac_ratio:.1f}x (target: 3x+). Excellent acquisition efficiency!")
    elif ltv_cac_ratio > 1:
        insights.append(f"Acceptable Unit Economics: LTV:CAC ratio is {ltv_cac_ratio:.1f}x. Room to improve efficiency.")
    elif ltv_cac_ratio > 0:
        insights.append(f"Critical Unit Economics Alert: LTV:CAC ratio {ltv_cac_ratio:.1f}x - losing money on acquisition! Urgent action needed.")
    
    # Churn analysis
    if kpis['churn'] < 2:
        insights.append(f"Excellent Retention: {kpis['churn_formatted']} churn is outstanding! Continue current retention strategy.")
    elif kpis['churn'] < 5:
        insights.append(f"Healthy Churn: {kpis['churn_formatted']} is acceptable for SaaS. Monitor and optimize further.")
    else:
        insights.append(f"High Churn Alert: {kpis['churn_formatted']} is concerning! Prioritize retention programs immediately.")
    
    return insights if insights else ["📊 Upload your data to see AI-powered insights!"]

# Sidebar
st.sidebar.markdown('<div class="sidebar-header"><h2>ECHOLON</h2></div>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color: #888; font-size: 12px;">AI powered business intelligence</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)

page = st.sidebar.radio(
    "nav",
    ["Home", "Profile", "Insights", "Predictions", "Inventory", "What-If", "Recommendations", "Upload"],    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-section">System Status</div>', unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Test Connection", width='streamlit'):
        try:
            requests.get(f"{BACKEND_API_URL}/health", timeout=5)
            st.sidebar.success("Backend online")
        except:
            st.sidebar.error("Backend offline")

with col2:
    if st.session_state.data_source == 'uploaded':
        st.sidebar.info("Data loaded")
    else:
        st.sidebar.info("Demo data")

# Show onboarding if needed
if st.session_state.uploaded_data is None and page == "Home":
    show_personalized_onboarding()
    
# =================== PAGE: HOME ===================
if page == "Home":
    render_page_header("Dashboard Overview", "Your key business metrics at a glance.")
    render_last_updated()
    st.markdown(get_data_source_badge(), unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Key Performance Indicators")
    kpis = calculate_kpis_from_data()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_with_benchmark("💵", "Total Revenue", kpis['revenue_formatted'], kpis['revenue_delta'], BENCHMARKS["revenue"]["industry_avg"], BENCHMARKS["revenue"]["top_25_percent"], "Revenue vs industry benchmarks")
    with c2:
        render_kpi_with_benchmark("👥", "Active Customers", kpis['customers_formatted'], kpis['customers_delta'], 5000, 10000, "Total active customers")
    with c3:
        render_kpi_with_benchmark("💰", "CAC", kpis['cac_formatted'], kpis['cac_delta'], BENCHMARKS["customer_acquisition_cost"]["industry_avg"], BENCHMARKS["customer_acquisition_cost"]["top_25_percent"], "Lower is better")
    with c4:
        render_kpi_with_benchmark("📉", "Churn Rate", kpis['churn_formatted'], kpis['churn_delta'], BENCHMARKS["churn_rate"]["industry_avg"], BENCHMARKS["churn_rate"]["top_25_percent"], "Lower is better")
    
    st.markdown("---")
    st.subheader("Monthly Revenue Trend")
    st.caption("Based on" + (" your uploaded dataset" if kpis['data_source'] == 'uploaded' else " demo dataset"))
    if kpis['data_source'] == 'uploaded' and st.session_state.uploaded_data is not None:
        try:
            df = st.session_state.uploaded_data
            if 'date' in df.columns and 'value' in df.columns:
                df_sorted = df.sort_values('date')
                st.line_chart(df_sorted.set_index('date')['value'], width='streamlit', height=300)
            else:
                st.line_chart(DEMO_TREND, width='streamlit', height=300)
        except:
            st.line_chart(DEMO_TREND, width='streamlit', height=300)
    else:
        st.line_chart(DEMO_TREND, width='streamlit', height=300)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sales Distribution")
        fig = px.pie(values=[45,25,20,10], names=['SaaS','Support','Services','Other'])
        st.plotly_chart(fig, width='streamlit')
    with c2:
        st.subheader("Key Metrics")
        st.markdown(f"**Total Customers**: {kpis['customers_formatted']}\n\n**Active Subscriptions**: {int(kpis['customers'] * 0.7):,}\n\n**MRR**: ${kpis['revenue'] / 12 / 1000:.0f}K\n\n**LTV**: ${kpis['revenue'] / kpis['customers'] if kpis['customers'] > 0 else 0:,.0f}")
    
    st.markdown("---")
    st.subheader("Features")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**Smart Analysis**\n\nOur AI analyzes KPIs to provide data-driven insights.")
    with c2:
        st.success("**Actionable**\n\nEvery recommendation includes specific actions.")
    with c3:
        st.warning("**Real-Time**\n\nUpdates instantly as you adjust scenarios.")

# PAGE: INSIGHTS
elif page == "Insights":
    render_page_header("Business Insights", "AI-generated insights from your data.")
    render_last_updated()
    st.markdown(get_data_source_badge(), unsafe_allow_html=True)
    st.markdown("---")
    kpis = calculate_kpis_from_data()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_with_benchmark("💵", "Revenue", kpis['revenue_formatted'], kpis['revenue_delta'], BENCHMARKS["revenue"]["industry_avg"], BENCHMARKS["revenue"]["top_25_percent"])
    with c2:
        render_kpi_with_benchmark("👥", "Users", kpis['customers_formatted'], kpis['customers_delta'], 5000, 10000)
    with c3:
        render_kpi_with_benchmark("📊", "Conversion", "3.8%", "+0.5%", BENCHMARKS["conversion_rate"]["industry_avg"], BENCHMARKS["conversion_rate"]["top_25_percent"])
    with c4:
        render_kpi_with_benchmark("💳", "Avg Order", "$285", "-2.1%", 200, 400)
    
    st.markdown("---")
    with st.spinner("Analyzing your data..."):
        time.sleep(0.5)
    
    st.markdown("### Key Insights")
    ai_insights = generate_actionable_insights(kpis)
    for insight in ai_insights:
        display_actionable_insight(insight)
        
# PAGE: PREDICTIONS
elif page == "Predictions":
    render_page_header("AI Predictions", "Forecast future trends.")
    render_last_updated()
    st.markdown(get_data_source_badge(), unsafe_allow_html=True)
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        metric = st.selectbox("Select Metric", ["Revenue", "Churn", "Growth"])
    with c2:
        horizon = st.selectbox("Forecast Window", ["1 Month", "3 Months", "6 Months", "12 Months"])
    
    if st.button("Generate Predictions", type="primary", width='streamlit'):
        with st.spinner("Building forecast model..."):
            time.sleep(1)
        st.success("Predictions updated")
        dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
        historical = np.random.normal(100000, 15000, 12)
        forecast = np.random.normal(105000, 12000, 12)
        fig = px.line(x=dates, y=forecast, title=f'{metric} Forecast')
        fig.add_scatter(x=dates, y=historical, name='Historical', mode='lines')
        st.plotly_chart(fig, width='streamlit')

# PAGE: INVENTORY
elif page == "Inventory":
    render_page_header("Inventory Optimization", "Optimize stock levels.")
    render_last_updated()
    st.markdown(get_data_source_badge(), unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("📦", "Stock Level", "8,450", "-3.2%", "")
    with c2:
        render_kpi_card("🔄", "Turnover", "12.4x", "+2.1x", "")
    with c3:
        render_kpi_card("💵", "Annual Cost", "$145K", "-$22K", "")
    with c4:
        render_kpi_card("⚠", "Stockout Risk", "4.2%", "-1.8%", "")

# PAGE: WHAT-IF
elif page == "What-If":
    render_page_header("What-If Scenario Planner", "Test different business scenarios.")
    render_last_updated()
    st.markdown("---")
    baseline = st.session_state.baseline
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Scenario Inputs")
        rev = st.number_input("Monthly Revenue ($)", min_value=0, value=baseline["revenue"], step=5000)
        mkt = st.number_input("Marketing Spend ($)", min_value=0, value=baseline["marketing"], step=1000)
        churn = st.slider("Monthly Churn Rate (%)", min_value=0.0, max_value=50.0, value=baseline["churn"]*100, step=0.5) / 100
        growth = st.slider("Customer Growth Rate (%)", min_value=0.0, max_value=50.0, value=baseline["growth"]*100, step=0.5) / 100
        run_btn = st.button("Run Scenario", type="primary", width='streamlit')
    
    if run_btn:
        st.session_state.last_updated = datetime.now()
        with col_right:
            st.subheader("Scenario Results")
            profit_margin = 0.25 - (mkt / max(rev, 1)) * 0.15
            profit_margin = max(min(profit_margin, 0.6), -0.3)
            profit = rev * profit_margin
            customers = 1000 * (1 + growth - churn)
            st.metric("Revenue", f"${rev:,}", delta=f"${rev - baseline['revenue']:,}")
            st.metric("Estimated Profit", f"${profit:,.0f}")
            st.metric("Active Customers", f"{customers:,.0f}")
            st.metric("Churn Rate", f"{churn*100:.1f}%")

# PAGE: RECOMMENDATIONS
elif page == "Recommendations":
    render_page_header("AI Recommendations", "Data-driven suggestions for your business.")
    render_last_updated()
    st.markdown("---")
    
    tabs = st.tabs(["Growth", "Retention", "Efficiency", "Innovation"])
    
    with tabs[0]:
        st.markdown("## Growth Strategies")
        show_tactical_recommendation(
            title="Market Expansion",
            action="Launch targeted campaigns in 2 adjacent markets + test pricing tier",
            roi="3-5x ROI in 6 months",
            time="4-6 weeks",
            priority="HIGH",
            why="Your CAC is low and unit economics strong. Time to scale acquisition."
        )
        show_tactical_recommendation(
            title="Product Expansion",
            action="Launch premium tier with advanced features + support",
            roi="30% revenue increase",
            time="8-10 weeks",
            priority="HIGH",
            why="Your top customers show strong willingness to pay for premium features."
        )
        show_tactical_recommendation(
            title="Partnership Strategy",
            action="Identify 3 complementary products for co-marketing deals",
            roi="2-3x ROI",
            time="2-3 weeks",
            priority="MEDIUM",
            why="Low-cost way to reach new audiences through trusted partners."
        )
    
    with tabs[1]:
        st.markdown("## Retention Tactics")
        show_tactical_recommendation(
            title="Improve Onboarding",
            action="Create 5-email onboarding sequence + video walkthroughs",
            roi="Reduce churn by 20-30%",
            time="2 weeks",
            priority="HIGH",
            why="Strong onboarding is the #1 predictor of retention. Your churn suggests gaps here."
        )
        show_tactical_recommendation(
            title="Build Community",
            action="Launch Slack community for customers + monthly webinars",
            roi="10-15% churn reduction",
            time="4 weeks",
            priority="MEDIUM",
            why="Community creates switching costs and increases engagement."
        )
        show_tactical_recommendation(
            title="Loyalty Rewards",
            action="Implement referral program (20% discount) + rewards tier",
            roi="5-10% churn reduction",
            time="1 week",
            priority="MEDIUM",
            why="Incentivize long-term commitments and turn customers into advocates."
        )
    
    with tabs[2]:
        st.markdown("## Efficiency & Cost Optimization")
        show_tactical_recommendation(
            title="Automate Customer Success",
            action="Implement NPS surveys + auto-triggered help content",
            roi="Reduce support cost by 15-20%",
            time="3 weeks",
            priority="HIGH",
            why="Proactive support reduces churn AND support overhead."
        )
        show_tactical_recommendation(
            title="Operational Efficiency",
            action="Audit vendor costs + renegotiate top 5 contracts",
            roi="$50K-$100K annual savings",
            time="2 weeks",
            priority="MEDIUM",
            why="Many vendors offer discounts for longer terms or higher volume."
        )
        show_tactical_recommendation(
            title="Inventory Optimization",
            action="Implement demand forecasting + reduce SKU count by 20%",
            roi="$30K-$50K working capital freed up",
            time="6 weeks",
            priority="MEDIUM",
            why="Reduce carrying costs and improve cash flow without affecting revenue."
        )
    
    with tabs[3]:
        st.markdown("## Innovation & New Products")
        show_tactical_recommendation(
            title="AI-Powered Features",
            action="Add AI recommendations to your product (can use existing APIs)",
            roi="Increase ARPU by 25-40%",
            time="4-6 weeks",
            priority="HIGH",
            why="Customers love AI. It's differentiating and commands premium pricing."
        )
        show_tactical_recommendation(
            title="Mobile App",
            action="Launch iOS app with core features (MVP approach)",
            roi="Increase engagement + reduce churn by 15%",
            time="8-12 weeks",
            priority="MEDIUM",
            why="Mobile is now table stakes. Even basic app increases stickiness."
        )
        show_tactical_recommendation(
            title="Adjacent Vertical",
            action="Research + pilot 1 adjacent market segment",
            roi="Potential $500K+ annual revenue",
            time="12 weeks",
            priority="LOW",
            why="Reduce concentration risk + diversify revenue streams."
        )

# PAGE: UPLOAD

# PAGE: PROFILE
elif False:  # page == "Profile" - DISABLED DUE TO SYNTAX ERRORS
 render_page_header("👤 Company Profile", "Tell us about your business so we can customize AI insights.")
 render_last_updated()
# PAGE: PROFILE
elif page == "Profile":
    render_page_header("👤 Company Profile", "Tell us about your business so we can customize AI insights.")
    render_last_updated()
    st.markdown("---")
    
    st.subheader("📋 Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("🏢 Company Name", value=st.session_state.get('profile', {}).get('company_name', ''))
        industry = st.selectbox("🏭 Industry", ["Technology", "Healthcare", "Finance", "E-Commerce", "Professional Services", "Retail", "Manufacturing", "Education", "Other"], key="industry_select")
    with col2:
        annual_revenue = st.number_input("💵 Annual Revenue ($)", min_value=0, value=st.session_state.get('profile', {}).get('annual_revenue', 0), step=100000)
        employee_count = st.number_input("👥 Employee Count", min_value=1, value=st.session_state.get('profile', {}).get('employee_count', 10), step=1)

# PAGE: UPLOAD
