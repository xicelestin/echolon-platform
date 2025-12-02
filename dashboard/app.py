import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import os

st.set_page_config(page_title="Echolon AI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

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
.feature-card {background: rgba(255,149,0,0.08); border: 1px solid #ff9500; border-radius: 8px; padding: 20px; transition: all 0.3s;}
.feature-card:hover {background: rgba(255,149,0,0.15); border-color: #ffb84d; box-shadow: 0 4px 16px rgba(255,149,0,0.15);}
.page-header h1 {font-size: 36px; font-weight: 700; margin: 0; letter-spacing: -0.5px;}
.page-header p {font-size: 14px; color: #a0a0a0; margin: 8px 0 0 0;}
.last-updated {font-size: 12px; color: #888; text-align: right; padding: 12px 0;}
hr {border: none; border-top: 1px solid #1a1f38; margin: 24px 0;}
</style>
""", unsafe_allow_html=True)
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'demo'
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = datetime.now()
if 'baseline' not in st.session_state:
    st.session_state.baseline = {"revenue": 100000, "marketing": 20000, "churn": 0.05, "growth": 0.08, "inventory": 1000}

def render_last_updated():
    now = datetime.now()
    diff = (now - st.session_state.last_updated).total_seconds()
    time_text = "just now" if diff < 60 else f"{int(diff//60)} min ago" if diff < 3600 else f"{int(diff//3600)} hrs ago"
    st.markdown(f"<div class='last-updated'>Last updated: {time_text}</div>", unsafe_allow_html=True)

def render_kpi_card(icon, title, metric, delta):
    st.markdown(f"<div class='kpi-card'><div class='icon'>{icon}</div><div class='title'>{title}</div><div class='metric'>{metric}</div><div class='delta'>{delta}</div></div>", unsafe_allow_html=True)

def render_page_header(title, subtitle):
    st.markdown(f"<div class='page-header'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)

st.sidebar.markdown("<div class='sidebar-header'><h2>ECHOLON</h2><p>AI powered business intelligence</p></div>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-section'>Navigation</div>", unsafe_allow_html=True)

page = st.sidebar.radio("nav", ["Home", "Insights", "Predictions", "Inventory", "What-If", "Recommendations", "Upload"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-section'>System</div>", unsafe_allow_html=True)
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Check Connection", use_container_width=True):
        try:
            requests.get(f"{BACKEND_API_URL}/health", timeout=5)
            st.sidebar.success("Backend LIVE")
        except:
            st.sidebar.error("Connection failed")
with col2:
    if st.button("Manage App", use_container_width=True):
        st.sidebar.info("App panel")

st.sidebar.markdown("---")
st.sidebar.success("Connected to data") if st.session_state.data_source == 'uploaded' else st.sidebar.info("Using demo data")

if page == "Home":
    render_page_header("Welcome Back", "Echolon AI Dashboard")
    render_last_updated()
    st.markdown("---")
    st.subheader("Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi_card("💵", "Revenue Growth", "+15.3%", "Up 3.1%")
    with c2: render_kpi_card("👤", "Customer Growth", "+1.8%", "Up 0.5%")
    with c3: render_kpi_card("💰", "Acquisition Cost", "$241K", "Down 2%")
    with c4: render_kpi_card("📉", "Churn Rate", "2.3%", "Down 0.3%")
    
    st.markdown("---")
    st.subheader("Revenue Overview")
    demo_data = pd.DataFrame({'Week': ['Nov','Dec','Jan','Feb','Mar','Apr','May','Jun'], 'Revenue': [45000,48000,52000,51000,55000,58000,62000,60000]}).set_index('Week')
    st.line_chart(demo_data, use_container_width=True, height=300)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sales by Category")
        fig = px.pie(values=[45,25,20,10], names=['SaaS','Support','Services','Other'])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Key Metrics")
        st.markdown("**Total Customers**: 1,248\n**Active Subscriptions**: 892\n**MRR**: $487K\n**LTV**: $12,450")
    
    st.markdown("---")
    st.subheader("AI-Powered Recommendations")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("📊 **Smart Analysis**\nOur AI analyzes KPIs to provide data-driven insights.")
    with c2: st.success("🎯 **Actionable**\nEvery recommendation includes specific actions.")
    with c3: st.warning("⚡ **Real-Time**\nUpdates instantly as you adjust scenarios.")

elif page == "Insights":
    render_page_header("Business Insights", "AI-generated insights from your data")
    render_last_updated()
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi_card("💵", "Revenue", "$2.4M", "12.5%")
    with c2: render_kpi_card("👥", "Users", "8,432", "8.2%")
    with c3: render_kpi_card("📊", "Conversion", "3.8%", "0.5%")
    with c4: render_kpi_card("💳", "Avg Order", "$285", "-2.1%")

elif page == "Predictions":
    render_page_header("AI Predictions", "Forecast key metrics")
    render_last_updated()
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: metric = st.selectbox("Metric", ["Revenue", "Churn", "Growth"])
    with c2: horizon = st.selectbox("Horizon", ["1M", "3M", "6M"])
    if st.button("Generate", type="primary", use_container_width=True):
        st.success("Predictions generated!")

elif page == "Inventory":
    render_page_header("Inventory Optimization", "Reduce costs and optimize stock")
    render_last_updated()
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi_card("📋", "Stock Level", "8,450", "-3.2%")
    with c2: render_kpi_card("🔄", "Turnover", "12.4x", "+2.1x")
    with c3: render_kpi_card("💵", "Annual Cost", "$145K", "-$22K")
    with c4: render_kpi_card("⚠", "Stockout Risk", "4.2%", "-1.8%")

elif page == "What-If":
    render_page_header("What-If Scenario Planner", "Model and compare business outcomes")
    render_last_updated()
    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("Inputs")
        rev = st.number_input("Revenue", 0, value=100000, step=1000)
        mkt = st.number_input("Marketing", 0, value=20000, step=1000)
        churn = st.slider("Churn", 0.0, 0.5, 0.05, 0.01)
        growth = st.slider("Growth", 0.0, 0.5, 0.08, 0.01)
        if st.button("Run", type="primary", use_container_width=True):
            st.session_state.last_updated = datetime.now()
    with c_right:
        st.subheader("Results")
        profit = rev * (0.25 - (mkt / max(rev, 1)) * 0.1)
        customers = 1000 * (1 + growth - churn)
        c_a, c_b = st.columns(2)
        with c_a:
            st.metric("Revenue", f"${rev:,}", f"${rev-100000:,}")
            st.metric("Profit", f"${profit:,.0f}", f"${profit-25000:,.0f}")
        with c_b:
            st.metric("Customers", f"{customers:,.0f}", f"{customers-1030:,.0f}")
            st.metric("Churn", f"{churn*100:.1f}%")

elif page == "Recommendations":
    render_page_header("AI Recommendations", "Data-driven actions to improve business")
    render_last_updated()
    st.markdown("---")
    tabs = st.tabs(["Growth", "Retention", "Efficiency", "Innovation"])
    with tabs[0]: st.markdown("- Market expansion\n- Revenue optimization\n- New channels")
    with tabs[1]: st.markdown("- Churn prevention\n- Engagement programs\n- Loyalty rewards")
    with tabs[2]: st.markdown("- Cost reduction\n- Process automation\n- Resource optimization")
    with tabs[3]: st.markdown("- New products\n- Technology\n- Strategic partnerships")

elif page == "Upload":
    render_page_header("Upload Your Data", "Upload CSV for analysis")
    st.markdown("---")
    uploaded_file = st.file_uploader("Choose CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.uploaded_data = df
        st.session_state.data_source = 'uploaded'
        st.session_state.last_updated = datetime.now()
        st.success(f"Uploaded! {df.shape[0]} rows x {df.shape[1]} columns")
        st.dataframe(df.head(10), use_container_width=True)
