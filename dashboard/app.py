
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import os
import io
import numpy as np
from recommendations_handler import render_recommendations_panel

# Page configuration
st.set_page_config(
    page_title="Echolon AI - Business Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove emojis from sidebar as per requirement
st.markdown("""
    <style>
    .sidebar .sidebar-content { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# Backend API URL (configure based on environment)
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Initialize session state for data tracking
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

if 'data_source' not in st.session_state:
    st.session_state.data_source = 'demo'  # 'demo' or 'uploaded'

if 'api_response' not in st.session_state:
    st.session_state.api_response = None

# Scenario history and comparison
if 'scenario_history' not in st.session_state:
    st.session_state.scenario_history = []

if 'scenario_name' not in st.session_state:
    st.session_state.scenario_name = None

# Sidebar navigation - NO EMOJIS
st.sidebar.title("ECHOLON")
st.sidebar.markdown("AI powered business intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
        ["Home", "Upload Data", "Insights", "Predictions", "Inventory Optimization", "What-If"])

st.sidebar.markdown("---")

# Check backend connection button
if st.sidebar.button("Check Backend Connection"):
    try:
        res = requests.get(f"{BACKEND_API_URL}/health", timeout=5)
        if res.status_code == 200:
            st.sidebar.success("Backend is LIVE")
        else:
            st.sidebar.warning(f"Backend returned {res.status_code}")
    except Exception as e:
        st.sidebar.error(f"Could not connect: {str(e)}")

# ============= HOME PAGE =============
if page == "Home":
    st.title("Welcome back")
    st.markdown("## Echolon AI Dashboard")
    
    # Data source indicator badge
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.session_state.data_source == 'uploaded':
            st.success("Connected to your uploaded data")
        else:
            st.info("Using demo data")
    
    st.markdown("---")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Revenue Growth", "+15.3%", "Up 3.1% from last month")
    with col2:
        st.metric("Customer Growth", "+1.8%", "Up 0.5% from last month")
    with col3:
        st.metric("Acquisition Cost", "$241K", "Down 2% from last month")
    with col4:
        st.metric("Churn Rate", "2.3%", "Down 0.3% from last month")
    
    st.markdown("---")
    
    # Revenue chart
    st.subheader("Revenue Overview")
    
    if st.session_state.data_source == 'uploaded' and st.session_state.uploaded_data is not None:
        # Use uploaded data if available
        df = st.session_state.uploaded_data
        if 'date' in df.columns and 'revenue' in df.columns:
            chart_data = df[['date', 'revenue']].set_index('date')
            st.line_chart(chart_data, use_container_width=True, height=300, color="#FF9500")
        else:
            st.warning("CSV must contain 'date' and 'revenue' columns for revenue chart")
    else:
        # Demo data
        demo_data = pd.DataFrame({
            'Week': ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
            'Revenue': [45000, 48000, 52000, 51000, 55000, 58000, 62000, 60000, 65000, 68000, 70000, 68000]
        }).set_index('Week')
        st.line_chart(demo_data, use_container_width=True, height=300, color="#FF9500")
    
    st.markdown("---")
    
    # Sales by category
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Category")
        sales_data = {
            'Category': ['SaaS', 'Support', 'Services', 'Other'],
            'Sales': [45, 25, 20, 10]
        }
        fig = px.pie(values=sales_data['Sales'], names=sales_data['Category'],
                     color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Key Metrics Summary")
        st.markdown("""
        **Total Customers**: 1,248
        
        **Active Subscriptions**: 892
        
        **Monthly Recurring Revenue**: $487K
        
        **Average Customer Lifetime Value**: $12,450
        """)
    
    st.markdown("---")
    

     # ----- AI Recommendations Feature Section -----
    st.markdown("---")
    st.subheader("✨ AI-Powered Recommendations")
    st.markdown("Get instant, scenario-specific business recommendations powered by our AI engine.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Smart Analysis**\n\nOur AI analyzes your KPIs, market trends, and business patterns to provide data-driven insights.")
    with col2:
        st.success("🎯 **Actionable Insights**\n\nEvery recommendation comes with specific actions you can take to improve your business.")
    with col3:
        st.warning("⚡ **Real-Time Updates**\n\nRecommendations update instantly as you adjust scenarios in the What-If planner.")
    
    st.markdown("Try our [What-If Scenario Planner](/?page=What-If) to see AI recommendations in action!")
    st.markdown("---")
    
# Bottom sections - Insights, Predictions, Forecasts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Insights")
        st.markdown("""
        **Connect your data to see AI-generated insights**
        
        Upload CSV data and our ML models will analyze patterns, trends, and anomalies in your business metrics.
        """)
    
    with col2:
        st.subheader("Predictions")
        st.markdown("""
        **Connect your data to see predictions**
        
        Get AI-powered forecasts for your key metrics including revenue, customer churn, and growth trends.
        """)
    
    with col3:
        st.subheader("Forecasts")
        st.markdown("""
        **Connect your data to see forecasts**
        
        Advanced scenario modeling to explore different business outcomes and optimize strategy.
        """)
    
    st.markdown("---")
    
    # AI Recommendations Panel
    with st.sidebar:
        st.markdown("---")
        render_recommendations_panel(
            BACKEND_API_URL, 
            st.session_state.data_source, 
            st.session_state.uploaded_data
        )

# ============= UPLOAD DATA PAGE =============
elif page == "Upload Data":
    st.title("Upload Your Data")
    st.markdown("Upload a CSV file containing your business data for analysis and AI-powered insights")
    
    st.markdown("---")
    
    # Sample CSV download
    st.subheader("Sample CSV Format")
    
    # Generate 30 days of sample data
    sample_df = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=30).strftime('%Y-%m-%d').tolist(),
        'revenue': [45000 + i*1000 + (i % 3)*500 for i in range(30)],
        'customers': [245 + i*2.5 for i in range(30)],
        'churn_rate': [2.1 + (i % 5)*0.05 for i in range(30)],
        'customer_acquisition_cost': [241000 - i*100 for i in range(30)],
        'customer_lifetime_value': [12450 + i*50 for i in range(30)],
        'support_tickets': [42 + (i % 7)*2 for i in range(30)],
        'product_a_sales': [18000 + i*200 for i in range(30)],
        'product_b_sales': [15000 + i*180 for i in range(30)],
        'product_c_sales': [12000 + i*150 for i in range(30)]
    })
    
    csv_buffer = io.StringIO()
    sample_df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    
    st.download_button(
        label="Download sample CSV (30 days of data)",
        data=csv_string,
        file_name="sample_data.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # File uploader
    st.subheader("Upload Your CSV")
    uploaded_file = st.file_uploader(
        "Drag and drop file here",
        type="csv",
        help="Limit 200MB per file"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Store in session state
            st.session_state.uploaded_data = df
            st.session_state.data_source = 'uploaded'
            
            st.success(f"File uploaded successfully! Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", df.shape[0])
            with col2:
                st.metric("Total Columns", df.shape[1])
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            
            # Send to backend
            if st.button("Process & Save to Backend", type="primary"):
                with st.spinner("Processing data..."):
                    try:
                        data_records = df.to_dict(orient="records")
                        response = requests.post(
                            f"{BACKEND_API_URL}/api/upload_csv",
                            json={"data": data_records},
                            timeout=30
                        )
                        if response.status_code == 200:
                            st.success("Data successfully processed and saved!")
                            st.session_state.api_response = response.json()
                        else:
                            st.error(f"Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend: {str(e)}")
                        st.info("Make sure the backend service is running")
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        st.info("Please upload a CSV file to begin")

# ============= INSIGHTS PAGE =============
elif page == "Insights":
    st.title("Business Insights Dashboard")
    st.markdown("Connect your data to see AI-generated insights and business intelligence")
    
    st.markdown("---")
    
    if st.session_state.data_source == 'uploaded':
        st.info("Insights connected to your uploaded data")
    else:
        st.info("Connect your data to see AI-generated insights")
    
    # Try to fetch from backend
    try:
        response = requests.get(f"{BACKEND_API_URL}/api/insights", timeout=10)
        if response.status_code == 200:
            insights_data = response.json()
            st.success("Connected to ML insights model")
    except Exception as e:
        st.warning(f"Could not connect to insights backend: {str(e)}")
    
    # Display key metrics
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", "$2.4M", "+12.5%")
    with col2:
        st.metric("Active Users", "8,432", "+8.2%")
    with col3:
        st.metric("Conversion Rate", "3.8%", "+0.5%")
    with col4:
        st.metric("Avg Order Value", "$285", "-2.1%")

# ============= PREDICTIONS PAGE =============
elif page == "Predictions":
    st.title("AI-Powered Predictions")
    st.markdown("Configure and generate predictions for your business metrics")
    
    st.markdown("---")
    
    st.subheader("Prediction Configuration")
    col1, col2 = st.columns(2)
    with col1:
        metric_to_predict = st.selectbox(
            "Select Metric",
            ["Revenue", "Customer Growth", "Churn Rate"]
        )
    with col2:
        prediction_horizon = st.selectbox(
            "Prediction Horizon",
            ["1 Month", "3 Months", "6 Months"]
        )
    
    if st.button("Generate Predictions", type="primary"):
        with st.spinner("Running ML model..."):
            try:
                response = requests.post(
                    f"{BACKEND_API_URL}/api/predictions",
                    json={
                        "metric": metric_to_predict,
                        "horizon": prediction_horizon
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    st.success("Predictions generated successfully!")
                else:
                    st.error(f"Prediction failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

                # ============= INVENTORY OPTIMIZATION PAGE =============
elif page == "Inventory Optimization":
    st.title("Inventory Optimization")
    st.markdown("Optimize your inventory levels and reduce holding costs with AI-powered insights")
    
    st.markdown("---")
    
    # KPI Metrics for Inventory
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Stock Level", "8,450 units", "-3.2% from target")
    with col2:
        st.metric("Inventory Turnover", "12.4x", "Up 2.1x from last year")
    with col3:
        st.metric("Holding Cost (Annual)", "$145K", "Down $22K from last quarter")
    with col4:
        st.metric("Stockout Risk", "4.2%", "Down 1.8% from average")
    
    st.markdown("---")
    
    # Inventory Analysis Section
    st.subheader("Inventory Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stock Level Trend")
        stock_trend = pd.DataFrame({
            'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
            'Stock': [8200, 8050, 8100, 8320, 8450, 8380, 8290, 8100]
        }).set_index('Week')
        st.line_chart(stock_trend, use_container_width=True, height=250, color="#FF9500")
    
    with col2:
        st.subheader("Inventory by Category")
        category_data = {
            'Category': ['Electronics', 'Textiles', 'Furniture', 'Other'],
            'Units': [3200, 2850, 1800, 600]
        }
        fig = px.pie(values=category_data['Units'], names=category_data['Category'],
                    color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Optimization Recommendations
    st.subheader("Optimization Recommendations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📊 **Slow-Moving Items**\n\nIdentified 127 SKUs with 0 sales in past 30 days. Recommended action: Liquidate or repurpose for $18K recovery potential.")
        st.warning("⚠️ **Overstock Alert**\n\nElectronics category is 22% above optimal level. Suggested: Promotional discount campaign.")
    
    with col2:
        st.success("✅ **Fast Movers**\n\nTop 12 products account for 64% of turnover. Increase safety stock levels by 15% to reduce stockout risk.")
        st.info("💰 **Cost Optimization**\n\nImplement FIFO tracking system to reduce spoilage by estimated $12K annually.")
    
    st.markdown("---")
    
    # Advanced Inventory Tools
    st.subheader("Inventory Tools & Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        reorder_point = st.slider("Reorder Point (days of inventory)", 5, 90, 30)
        safety_stock_pct = st.slider("Safety Stock Buffer (%)", 5, 50, 20)
    
    with col2:
        lead_time_days = st.number_input("Average Lead Time (days)", 1, 60, 14)
        holding_cost_pct = st.slider("Annual Holding Cost (%)", 5, 30, 15)
    
    if st.button("Calculate Optimal Inventory Level", type="primary", key="inventory_calc"):
        st.success(f"✅ Optimal inventory level calculated with {reorder_point}d reorder point and {safety_stock_pct}% safety buffer.")
        st.metric("Recommended Stock Level", f"{6500 + (reorder_point * 50):.0f} units")
        st.metric("Annual Holding Cost (Projected)", f"${145000 * (holding_cost_pct/15):.0f}")



# ============= WHAT-IF SCENARIO PLANNER PAGE =============
elif page == "What-If":
    st.title("What-If Scenario Planner")
    st.caption("Test business scenarios by adjusting key assumptions and comparing outcomes.")

    # Initialize baseline scenario in session state
    if "baseline" not in st.session_state:
        st.session_state.baseline = {
            "revenue": 100_000,
            "marketing": 20_000,
            "churn": 0.05,
            "growth": 0.08,
            "inventory": 1_000,
        }

    col_left, col_right = st.columns(2)

    # ----- Scenario inputs (LEFT COLUMN) -----
    with col_left:
        st.subheader("Scenario Inputs")

        revenue = st.number_input(
            "Monthly Revenue",
            min_value=0,
            value=int(st.session_state.baseline["revenue"]),
            step=1_000,
            help="Expected monthly revenue under this scenario.",
        )

        marketing = st.number_input(
            "Marketing Spend / CAC Proxy",
            min_value=0,
            value=int(st.session_state.baseline["marketing"]),
            step=1_000,
            help="Total monthly marketing spend or CAC proxy.",
        )

        churn = st.slider(
            "Churn Rate",
            min_value=0.0,
            max_value=0.5,
            value=float(st.session_state.baseline["churn"]),
            step=0.01,
            help="Fraction of customers leaving per month.",
        )

        growth = st.slider(
            "Customer Growth Rate",
            min_value=0.0,
            max_value=0.5,
            value=float(st.session_state.baseline["growth"]),
            step=0.01,
            help="Expected net customer growth per month.",
        )

        inventory = st.number_input(
            "Inventory Level",
            min_value=0,
            value=int(st.session_state.baseline["inventory"]),
            step=100,
            help="Units available or safety stock level.",
        )

        run = st.button("Run Scenario", type="primary")

    # ----- Scenario calculation -----
    def run_model(revenue, marketing, churn, growth, inventory):
        profit_margin = 0.25 - (marketing / max(revenue, 1)) * 0.1
        profit_margin = max(min(profit_margin, 0.5), -0.5)
        profit = revenue * profit_margin
        customers = 1_000 * (1 + growth - churn)
        stockouts_risk = max(0.0, 1 - inventory / 1_000)
        months = np.arange(1, 13)
        projected_revenue = revenue * (1 + growth - churn) ** (months - 1)
        return {
            "revenue": revenue,
            "marketing": marketing,
            "churn": churn,
            "growth": growth,
            "inventory": inventory,
            "profit": profit,
            "customers": customers,
            "stockouts_risk": stockouts_risk,
            "months": months,
            "projected_revenue": projected_revenue,
        }

    baseline = run_model(
        st.session_state.baseline["revenue"],
        st.session_state.baseline["marketing"],
        st.session_state.baseline["churn"],
        st.session_state.baseline["growth"],
        st.session_state.baseline["inventory"],
    )

# Scenario always calculates based on current inputs (reactive)
    scenario = run_model(revenue, marketing, churn, growth, inventory)
    # ----- Scenario results (RIGHT COLUMN) -----
    with col_right:
        st.subheader("Scenario Results")

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Revenue (Scenario)", f"${scenario['revenue']:,.0f}", 
                      delta=f"${scenario['revenue']-baseline['revenue']:,.0f}")
            st.metric("Profit (Scenario)", f"${scenario['profit']:,.0f}",
                      delta=f"${scenario['profit']-baseline['profit']:,.0f}")
            st.metric("Customers (Scenario)", f"{scenario['customers']:,.0f}",
                      delta=f"{scenario['customers']-baseline['customers']:,.0f}")
        with col_b:
            st.metric("Churn Rate", f"{scenario['churn']*100:.1f}%",
                      delta=f"{(scenario['churn']-baseline['churn'])*100:.1f} pp")
            st.metric("Growth Rate", f"{scenario['growth']*100:.1f}%",
                      delta=f"{(scenario['growth']-baseline['growth'])*100:.1f} pp")
            st.metric("Stockout Risk", f"{scenario['stockouts_risk']*100:.1f}%")

        # Revenue projection chart
        proj_df = pd.DataFrame({
            "Month": scenario["months"],
            "Baseline": baseline["projected_revenue"],
            "Scenario": scenario["projected_revenue"],
        })
        st.line_chart(proj_df.set_index("Month"))

    st.markdown("---")

    # ----- AI Scenario Recommendations (SEPARATE SECTION) -----
    st.subheader("AI Scenario Recommendations")

    recs = []

    if scenario["churn"] > baseline["churn"] + 0.02:
        recs.append(
            "Churn is higher than baseline; focus on retention programs, better onboarding, and customer support improvements."
        )
    if scenario["marketing"] > baseline["marketing"] * 1.2 and scenario["profit"] <= baseline["profit"]:
        recs.append(
            "Marketing spend is up but profit is not improving; review channel ROI and shift budget toward higher-ROAS campaigns."
        )
    if scenario["growth"] > baseline["growth"] + 0.05 and scenario["profit"] < baseline["profit"]:
        recs.append(
            "Growth is strong but margins are compressed; consider pricing adjustments or cost optimization to avoid unprofitable growth."
        )
    if scenario["stockouts_risk"] > 0.3:
        recs.append(
            "Stockout risk is elevated; increase safety stock, improve forecasting, or work with suppliers to reduce lead times."
        )

    if not recs:
        recs.append("This scenario looks close to your baseline; consider pushing one assumption more aggressively to uncover risks or opportunities.")

    for r in recs:
        st.markdown(f"• {r}")

    st.markdown("---")


# Footer
st.markdown("---")
st.markdown("""
© 2024 Echolon AI | Built with Streamlit & FastAPI
""")
