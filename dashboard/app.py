import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import os

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
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
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
    st.markdown('<p class="main-header">Welcome to Echolon AI</p>', unsafe_allow_html=True)
    # 🔍 Backend Health Check Button
    if st.button("Check Backend Connection"):
        try:
            res = requests.get(f"{BACKEND_API_URL}/health", timeout=5)
            if res.status_code == 200:
                st.success("Backend is LIVE 🔥")
            else:
                st.warning(f"Backend returned {res.status_code}")
        except Exception as e:
            st.error(f"Could not connect: {str(e)}")
            
    st.markdown("""
    ### Your Intelligent Business Analytics Platform
    
    Echolon AI helps you transform raw business data into actionable insights using 
    advanced analytics and AI-powered predictions.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div class="metric-card">
            <h3>📤 Upload Data</h3>
            <p>Seamlessly upload your business data in CSV format for analysis</p>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<div class="metric-card">
            <h3>📊 View Insights</h3>
            <p>Explore comprehensive metrics and visualizations of your business performance</p>
        </div>""", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""<div class="metric-card">
            <h3>🔍 AI Predictions</h3>
            <p>Get AI-powered predictions and forecasts for future business trends</p>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 Key Features")
    st.markdown("""
    - **Real-time Analytics**: Process and analyze data in real-time
    - **AI-Powered Insights**: Leverage machine learning for deeper understanding
    - **Secure & Scalable**: Built on Google Cloud Platform for enterprise-grade security
    - **Easy Integration**: RESTful API for seamless integration with existing systems
    """)

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
    <p>© 2024 Echolon AI | Built with ❤️ using Streamlit & FastAPI</p>
</div>
""", unsafe_allow_html=True)
