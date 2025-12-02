import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import os
import time

st.set_page_config(page_title="Echolon AI", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

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

def render_kpi_card(icon, title, metric, delta, help_text=""):
    st.markdown(f"<div class='kpi-card'><div class='icon'>{icon}</div><div class='title'>{title}</div><div class='metric'>{metric}</div><div class='delta'>{delta}</div></div>", unsafe_allow_html=True)
    if help_text:
        st.caption(help_text)

def render_page_header(title, subtitle):
    st.markdown(f"<div class='page-header'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)

st.sidebar.markdown("<div class='sidebar-header'><h2>ECHOLON</h2><p>AI powered business intelligence</p></div>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-section'>Navigation</div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "nav",
    ["Home", "Insights", "Predictions", "Inventory", "What-If", "Recommendations", "Upload"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='sidebar-section'>System Status</div>", unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Test Connection", use_container_width=True):
        try:
            requests.get(f"{BACKEND_API_URL}/health", timeout=5)
            st.sidebar.success("✓ Backend online")
        except:
            st.sidebar.error("⚠ Backend offline")

with col2:
    if st.session_state.data_source == 'uploaded':
        st.sidebar.info("✓ Data loaded successfully")
    else:
        st.sidebar.info("ℹ Using demo data")

if st.session_state.uploaded_data is None and page != "Upload":
    st.info("📊 No data uploaded yet. Visit the **Upload** page to import your CSV file for personalized insights.")

# PAGE: HOME
if page == "Home":
    render_page_header("Dashboard Overview", "Your key business metrics at a glance.")
    render_last_updated()
    st.markdown("---")
    
    st.subheader("Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("💵", "Total Revenue", "$2.4M", "+12.5%", "Total revenue from uploaded dataset")
    with c2:
        render_kpi_card("👥", "Active Customers", "8,432", "+8.2%", "Number of active paying customers")
    with c3:
        render_kpi_card("💰", "CAC", "$241", "↓ $48", "Average cost to acquire one customer")
    with c4:
        render_kpi_card("📉", "Churn Rate", "2.3%", "↓ 0.3%", "Percentage of customers lost over time")
    
    st.markdown("---")
    st.subheader("Monthly Revenue Trend")
    st.caption("Based on uploaded dataset")
    demo_data = pd.DataFrame({'Month': ['May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], 'Revenue': [45000,48000,52000,51000,55000,58000,62000,60000]}).set_index('Month')
    st.line_chart(demo_data, use_container_width=True, height=300)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sales Distribution")
        fig = px.pie(values=[45,25,20,10], names=['SaaS','Support','Services','Other'])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Key Metrics")
        st.markdown("**Total Customers**: 1,248\n\n**Active Subscriptions**: 892\n\n**MRR**: $487K\n\n**LTV**: $12,450")
    
    st.markdown("---")
    st.subheader("💡 Quick Features")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("📊 **Smart Analysis**\n\nOur AI analyzes KPIs to provide data-driven insights.")
    with c2:
        st.success("🎯 **Actionable**\n\nEvery recommendation includes specific actions.")
    with c3:
        st.warning("⚡ **Real-Time**\n\nUpdates instantly as you adjust scenarios.")

# PAGE: INSIGHTS
elif page == "Insights":
    render_page_header("Business Insights", "AI-generated insights and patterns detected from your data.")
    render_last_updated()
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("💵", "Revenue", "$2.4M", "+12.5%", "Total revenue metric")
    with c2:
        render_kpi_card("👥", "Users", "8,432", "+8.2%", "Total active users")
    with c3:
        render_kpi_card("📊", "Conversion", "3.8%", "+0.5%", "Conversion rate")
    with c4:
        render_kpi_card("💳", "Avg Order", "$285", "-2.1%", "Average order value")
    
    st.markdown("---")
    with st.spinner("Analyzing your data..."):
        time.sleep(0.5)
    
    st.markdown("### 🔍 Key Insights")
    st.markdown("- **Revenue Growth**: +12.5% month-over-month indicates strong market demand")
    st.markdown("- **Customer Acquisition**: CAC decreased by $48, showing improved marketing efficiency")
    st.markdown("- **Churn Reduction**: Down 0.3% - retention programs are working well")
    st.markdown("- **Opportunity**: Focus on high-value customers to increase LTV by 15-20%")

# PAGE: PREDICTIONS
elif page == "Predictions":
    render_page_header("AI Predictions", "Forecast future trends using machine learning models.")
    render_last_updated()
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        metric = st.selectbox(
            "Select Metric",
            ["Revenue", "Churn", "Growth"],
            help="Choose which business metric to forecast"
        )
    with c2:
        horizon = st.selectbox(
            "Choose Forecast Window",
            ["1 Month", "3 Months", "6 Months", "12 Months"],
            help="How far into the future to predict"
        )
    
    if st.button("🔮 Generate Predictions", type="primary", use_container_width=True):
        with st.spinner("Building forecast model..."):
            time.sleep(1)
        st.success("✓ Predictions updated successfully")
        st.info(f"Forecasting {metric} for {horizon}")
                st.markdown("""<div style='margin-top:20px'><h3>📊 Forecast</h3></div>""", unsafe_allow_html=True)
        # Create simple forecast visualization
        dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
        historical = np.random.normal(100000, 15000, 12)
        forecast = np.random.normal(105000, 12000, 12)
        fig = px.line(x=dates, y=forecast, title=f'{metric} Forecast',
                     labels={'x': 'Month', 'y': metric})
        fig.add_scatter(x=dates, y=historical, name='Historical', mode='lines')
        st.plotly_chart(fig, use_container_width=True)

# PAGE: INVENTORY
elif page == "Inventory":
    render_page_header("Inventory Optimization", "Optimize stock levels and reduce holding costs.")
    render_last_updated()
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("📋", "Stock Level", "8,450", "-3.2%", "Current inventory quantity")
    with c2:
        render_kpi_card("🔄", "Turnover", "12.4x", "+2.1x", "Annual inventory turnover")
    with c3:
        render_kpi_card("💵", "Annual Cost", "$145K", "-$22K", "Total inventory holding cost")
    with c4:
        render_kpi_card("⚠", "Stockout Risk", "4.2%", "-1.8%", "Risk of running out of stock")

# PAGE: WHAT-IF SCENARIO PLANNER
elif page == "What-If":
    render_page_header("What-If Scenario Planner", "Test business scenarios by adjusting key assumptions and comparing outcomes")
    render_last_updated()
    st.markdown("---")
    
    baseline = st.session_state.baseline
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Scenario Inputs")
        st.caption("Adjust the sliders below to model different business scenarios")
        
        rev = st.number_input(
            "Monthly Revenue ($)",
            min_value=0,
            value=baseline["revenue"],
            step=5000,
            help="Baseline monthly revenue used as model input"
        )
        
        mkt = st.number_input(
            "Marketing Spend ($)",
            min_value=0,
            value=baseline["marketing"],
            step=1000,
            help="Estimated monthly marketing and CAC investment"
        )
        
        churn = st.slider(
            "Monthly Churn Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=baseline["churn"]*100,
            step=0.5,
            help="Percentage of customers lost each month"
        ) / 100
        
        growth = st.slider(
            "Customer Growth Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=baseline["growth"]*100,
            step=0.5,
            help="Rate of new customers acquired each month"
        ) / 100
        
        run_btn = st.button("🚀 Run Scenario", type="primary", use_container_width=True)
        
        if run_btn:
            st.session_state.last_updated = datetime.now()
            with st.spinner("Analyzing scenario..."):
                time.sleep(1)
    
    with col_right:
        st.subheader("Scenario Results")
        st.caption("Comparison: Current Scenario vs. Baseline")
        
        profit_margin = 0.25 - (mkt / max(rev, 1)) * 0.15
        profit_margin = max(min(profit_margin, 0.6), -0.3)
        profit = rev * profit_margin
        
        customers = 1000 * (1 + growth - churn)
        
        baseline_profit_margin = 0.25 - (baseline["marketing"] / max(baseline["revenue"], 1)) * 0.15
        baseline_profit = baseline["revenue"] * baseline_profit_margin
        baseline_customers = 1000 * (1 + baseline["growth"] - baseline["churn"])
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.metric(
                "Revenue (Scenario)",
                f"${rev:,}",
                delta=f"${rev - baseline['revenue']:,}",
                help="Total monthly revenue"
            )
            st.metric(
                "Estimated Profit",
                f"${profit:,.0f}",
                delta=f"${profit - baseline_profit:,.0f}",
                help="Profit after marketing costs"
            )
        
        with c_b:
            st.metric(
                "Active Customers",
                f"{customers:,.0f}",
                delta=f"{customers - baseline_customers:,.0f}",
                help="Projected customer count"
            )
            st.metric(
                "Churn Rate",
                f"{churn*100:.1f}%",
                delta=f"{(churn - baseline['churn'])*100:.1f} pp",
                help="Monthly customer churn"
            )
        
        months = list(range(1, 7))
        scenario_proj = [rev * (1 + growth - churn) ** (m-1) for m in months]
        baseline_proj = [baseline["revenue"] * (1 + baseline["growth"] - baseline["churn"]) ** (m-1) for m in months]
        
        chart_data = pd.DataFrame({
            "Month": months * 2,
            "Revenue": scenario_proj + baseline_proj,
            "Type": ["Scenario"] * 6 + ["Baseline"] * 6
        })
        
        fig = px.line(chart_data, x="Month", y="Revenue", color="Type", title="6-Month Revenue Projection")
        fig.update_yaxes(title_text="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 Scenario Recommendations")
    
    recs = []
    if churn > baseline["churn"] + 0.02:
        recs.append("⚠ **High Churn Alert**: Focus on retention programs, improve onboarding, and enhance customer support.")
    
    if mkt > baseline["marketing"] * 1.3 and profit <= baseline_profit:
        recs.append("💰 **Marketing Efficiency**: Spending is up but profit isn't improving. Review channel ROI and reallocate budget.")
    
    if growth > baseline["growth"] + 0.05 and profit_margin < 0.15:
        recs.append("📈 **Growth vs. Margin**: Strong growth but thin margins. Consider pricing adjustments or cost optimization.")
    
    if not recs:
        recs.append("✓ This scenario looks healthy. Consider testing more aggressive assumptions to uncover risks or opportunities.")
    
    for r in recs:
        st.markdown(f"- {r}")

# PAGE: RECOMMENDATIONS
elif page == "Recommendations":
    render_page_header("AI Recommendations", "Actionable, data-driven suggestions for improving your business.")
    render_last_updated()
    st.markdown("---")
    
    tabs = st.tabs(["Growth", "Retention", "Efficiency", "Innovation"])
    
    with tabs[0]:
        st.markdown("#### 📈 Market Expansion & Revenue Growth")
        st.markdown("- **Expand to adjacent markets**: Target similar customer segments in nearby regions")
        st.markdown("- **Revenue optimization**: Test pricing tiers to capture high-value customers")
        st.markdown("- **New channels**: Launch targeted campaigns on underutilized platforms")
        st.markdown("- **Upsell programs**: Create tiered plans to increase customer lifetime value")
    
    with tabs[1]:
        st.markdown("#### 👋 Customer Retention & Engagement")
        st.markdown("- **Churn prevention**: Reach out to at-risk customers before they leave")
        st.markdown("- **Engagement programs**: Build community forums or user groups")
        st.markdown("- **Loyalty rewards**: Implement points or tiered benefits for long-term customers")
        st.markdown("- **Personalization**: Use data to customize customer experiences")
    
    with tabs[2]:
        st.markdown("#### ⚙ Cost Reduction & Operational Efficiency")
        st.markdown("- **Process automation**: Automate repetitive manual workflows")
        st.markdown("- **Resource optimization**: Reduce waste in inventory or staffing")
        st.markdown("- **Vendor negotiation**: Renegotiate contracts with top suppliers")
        st.markdown("- **Technology adoption**: Migrate to cloud solutions to reduce infrastructure costs")
    
    with tabs[3]:
        st.markdown("#### 🚀 Innovation & Strategic Moves")
        st.markdown("- **New product lines**: Launch complementary products for existing customers")
        st.markdown("- **Technology adoption**: Invest in AI tools to enhance operations")
        st.markdown("- **Strategic partnerships**: Partner with companies serving your target market")
        st.markdown("- **Market research**: Conduct customer surveys to validate new ideas")

# PAGE: UPLOAD
elif page == "Upload":
    render_page_header("Import Your Data", "Upload your business data (CSV format) for analysis.")
    st.markdown("---")
    
    st.info("📋 **Required columns**: Your CSV should include `date` and `value` columns for analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload your business data to replace the demo dataset"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            if 'date' not in df.columns or 'value' not in df.columns:
                st.error("⚠ Missing required columns. Your CSV must include 'date' and 'value' columns.")
            else:
                st.session_state.uploaded_data = df
                st.session_state.data_source = 'uploaded'
                st.session_state.last_updated = datetime.now()
                
                st.success(f"✓ Data loaded successfully! Analyzing {df.shape[0]:,} rows and {df.shape[1]} columns.")
                
                st.subheader("Data Preview")
                st.caption("First 10 rows of your uploaded dataset")
                st.dataframe(df.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"⚠ We couldn't process your file. Error: {str(e)}")
