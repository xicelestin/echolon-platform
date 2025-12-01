import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os
import random

# Page configuration
st.set_page_config(
    page_title="Echolon AI - Business Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    .kpi-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-change-positive {
        color: #10b981;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .kpi-change-negative {
        color: #ef4444;
        font-size: 0.9rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Backend API URL (configure based on environment)
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Sidebar navigation
st.sidebar.title("🚀 Echolon AI")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📤 Upload Data", "📊 Insights", "🔍 Predictions"]
)
st.sidebar.markdown("---")
st.sidebar.info("**Version:** 1.0.0\n\n**Status:** Active")

# ============= HOME PAGE =============
if page == "🏠 Home":
    # Professional Dashboard Header
    st.markdown('<p class="main-header">Business Intelligence Dashboard</p>', unsafe_allow_html=True)
    st.markdown("**Real-time insights and analytics for data-driven decisions**")
    st.markdown("---")
    
    # Generate mock data for demonstration
    def generate_mock_data():
        # KPI Metrics
        revenue = 2847650
        revenue_growth = 18.4
        customers = 8947
        customer_growth = 12.8
        mrr = 284500
        mrr_growth = 15.2
        churn = 2.8
        churn_change = -0.4
        
        # Revenue trend data
        dates = [(datetime.now() - timedelta(days=30-i)) for i in range(31)]
        base_revenue = 85000
        revenues = [base_revenue + (i * 1200) + random.randint(-5000, 8000) for i in range(31)]
        
        # Category distribution
        categories = ["Enterprise", "Professional", "Starter", "Free Trial"]
        cat_values = [45, 30, 18, 7]
        
        return {
            "revenue": revenue,
            "revenue_growth": revenue_growth,
            "customers": customers,
            "customer_growth": customer_growth,
            "mrr": mrr,
            "mrr_growth": mrr_growth,
            "churn": churn,
            "churn_change": churn_change,
            "dates": dates,
            "revenues": revenues,
            "categories": categories,
            "cat_values": cat_values
        }
    
    data = generate_mock_data()
    
    # KPI Metrics Row
    st.subheader("📊 Key Performance Indicators")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Revenue</div>
                <div class="kpi-value">${data['revenue']:,.0f}</div>
                <div class="kpi-change-positive">▲ {data['revenue_growth']}% vs last month</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with kpi2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Active Customers</div>
                <div class="kpi-value">{data['customers']:,}</div>
                <div class="kpi-change-positive">▲ {data['customer_growth']}% growth</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with kpi3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Monthly Recurring Revenue</div>
                <div class="kpi-value">${data['mrr']:,.0f}</div>
                <div class="kpi-change-positive">▲ {data['mrr_growth']}% increase</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with kpi4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Churn Rate</div>
                <div class="kpi-value">{data['churn']}%</div>
                <div class="kpi-change-positive">▼ {abs(data['churn_change'])}% improvement</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Revenue Overview (Last 30 Days)")
        # Create revenue trend chart
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Scatter(
            x=data['dates'],
            y=data['revenues'],
            mode='lines+markers',
            name='Daily Revenue',
            line=dict(color='#667eea', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        fig_revenue.update_layout(
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            hovermode='x unified',
            height=350,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Revenue by Plan")
        # Create pie chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=data['categories'],
            values=data['cat_values'],
            hole=0.4,
            marker_colors=['#667eea', '#764ba2', '#f093fb', '#4facfe']
        )])
        fig_pie.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Insights and Actions Row
    insight1, insight2, insight3 = st.columns(3)
    
    with insight1:
        st.markdown("""
        <div class="metric-card">
            <h3>💡 AI Insight</h3>
            <p>Customer acquisition cost decreased by 23% this quarter. Strong performance in digital channels.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight2:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Prediction</h3>
            <p>Revenue forecast shows 12% growth for next month based on current trends and seasonality.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Quick Action</h3>
            <p>Review high-value accounts due for renewal this week. 15 accounts worth $120K MRR.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("📋 Recent Activity")
    activity_data = pd.DataFrame({
        "Timestamp": [
            "2 minutes ago",
            "15 minutes ago",
            "1 hour ago",
            "3 hours ago",
            "Yesterday"
        ],
        "Activity": [
            "New customer signup - Enterprise Plan ($2,500/mo)",
            "Data uploaded - Q4_Sales_Report.csv (1,450 rows)",
            "Prediction completed - Revenue forecast for December",
            "Report exported - Monthly_KPI_Dashboard.pdf",
            "User invitation sent - jane.smith@example.com"
        ],
        "Status": ["✅ Success", "✅ Success", "✅ Success", "✅ Success", "⏳ Pending"]
    })
    st.dataframe(activity_data, use_container_width=True, hide_index=True)

# ============= UPLOAD DATA PAGE =============
elif page == "📤 Upload Data":
    st.markdown('<p class="main-header">Upload Business Data</p>', unsafe_allow_html=True)
    st.markdown("Upload your CSV file containing business data for analysis")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ File uploaded successfully! Shape: {df.shape[0]} rows × {df.shape[1]} columns")

            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)

            st.subheader("📈 Data Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", df.shape[0])
            with col2:
                st.metric("Total Columns", df.shape[1])
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())

            st.subheader("🔍 Column Information")
            col_info = pd.DataFrame({
                "Column Name": df.columns,
                "Data Type": df.dtypes.values,
                "Non-Null Count": df.count().values,
                "Null Count": df.isnull().sum().values
            })
            st.dataframe(col_info, use_container_width=True)

            # Upload to backend button
            if st.button("🚀 Process & Save to Backend", type="primary"):
                with st.spinner("Processing data..."):
                    try:
                        # Convert dataframe to records for API
                        data_records = df.to_dict(orient="records")
                        response = requests.post(
                            f"{BACKEND_API_URL}/api/upload_csv",
                            json={"data": data_records},
                            timeout=30
                        )
                        if response.status_code == 200:
                            st.success("✅ Data successfully processed and saved!")
                            st.json(response.json())
                        else:
                            st.error(f"❌ Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"❌ Failed to connect to backend: {str(e)}")
                        st.info("💡 Make sure the backend service is running")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    else:
        st.info("👆 Please upload a CSV file to begin")

# ============= INSIGHTS PAGE =============
elif page == "📊 Insights":
    st.markdown('<p class="main-header">Business Insights Dashboard</p>', unsafe_allow_html=True)

    # Fetch insights from backend
    try:
        response = requests.get(f"{BACKEND_API_URL}/api/insights", timeout=10)
        if response.status_code == 200:
            insights_data = response.json()

            # Display key metrics
            st.subheader("📊 Key Performance Indicators")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Revenue", "$2.4M", "+12.5%")
            with col2:
                st.metric("Active Users", "8,432", "+8.2%")
            with col3:
                st.metric("Conversion Rate", "3.8%", "+0.5%")
            with col4:
                st.metric("Avg Order Value", "$285", "-2.1%")

            st.markdown("---")

            # Sample visualizations
            st.subheader("📈 Trend Analysis")
            col1, col2 = st.columns(2)

            with col1:
                # Sample revenue trend
                dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
                revenue = [180000 + i * 15000 + (i % 3) * 10000 for i in range(12)]
                fig = px.line(x=dates, y=revenue, title="Monthly Revenue Trend")
                fig.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Sample category distribution
                categories = ["Product A", "Product B", "Product C", "Product D"]
                values = [35, 28, 22, 15]
                fig = px.pie(values=values, names=categories, title="Revenue by Category")
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("🏆 Top Performing Segments")

            # Sample data table
            performance_data = pd.DataFrame({
                "Segment": ["Enterprise", "SMB", "Startup", "Individual"],
                "Revenue": ["$980K", "$720K", "$450K", "$250K"],
                "Growth": ["+15%", "+22%", "+8%", "+5%"],
                "Customers": [45, 180, 340, 1200]
            })
            st.dataframe(performance_data, use_container_width=True)
        else:
            st.warning("⚠️ Could not fetch insights from backend")
            st.info("Displaying sample data for demonstration")
    except Exception as e:
        st.error(f"❌ Error connecting to backend: {str(e)}")
        st.info("💡 Make sure the backend service is running")

# ============= PREDICTIONS PAGE =============
elif page == "🔍 Predictions":
    st.markdown('<p class="main-header">AI-Powered Predictions</p>', unsafe_allow_html=True)
    st.markdown("Get intelligent forecasts and predictions for your business metrics")

    st.subheader("🎯 Prediction Configuration")
    col1, col2 = st.columns(2)

    with col1:
        metric_to_predict = st.selectbox(
            "Select Metric to Predict",
            ["Revenue", "User Growth", "Churn Rate", "Sales Volume"]
        )

    with col2:
        prediction_horizon = st.selectbox(
            "Prediction Horizon",
            ["7 Days", "30 Days", "90 Days", "1 Year"]
        )

    if st.button("🚀 Generate Predictions", type="primary"):
        with st.spinner("Running AI models..."):
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
                    predictions = response.json()
                    st.success("✅ Predictions generated successfully!")

                    # Display prediction results
                    st.subheader("📈 Forecast Results")

                    # Sample prediction visualization
                    dates = pd.date_range(start=datetime.now(), periods=30, freq="D")
                    actual = [100 + i * 2 for i in range(15)]
                    predicted = [130 + i * 2.5 for i in range(30)]

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates[:15], y=actual, name="Historical",
                        mode="lines+markers", line=dict(color="blue")
                    ))
                    fig.add_trace(go.Scatter(
                        x=dates[14:], y=predicted[14:], name="Predicted",
                        mode="lines+markers", line=dict(color="orange", dash="dash")
                    ))
                    fig.update_layout(
                        title=f"{metric_to_predict} Forecast - {prediction_horizon}",
                        xaxis_title="Date",
                        yaxis_title=metric_to_predict
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Confidence metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence Score", "87.5%")
                    with col2:
                        st.metric("Predicted Growth", "+18.2%")
                    with col3:
                        st.metric("Model Accuracy", "92.3%")
                else:
                    st.error(f"❌ Prediction failed: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Backend service may be unavailable")

    st.markdown("---")
    st.info("💡 **Note**: Predictions are generated using machine learning models trained on historical data. Accuracy improves with more data points and regular retraining.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
© 2024 Echolon AI | Built with ❤️ using Streamlit & FastAPI
</div>
""", unsafe_allow_html=True)
