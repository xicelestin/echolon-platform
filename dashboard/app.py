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

# Custom CSS for styling matching the mockup
st.markdown("""
<style>
    /* Clean minimal styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.2rem !important;
        font-weight: 400 !important;
        color: #666 !important;
        margin-bottom: 2rem !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #666;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Sidebar navigation
st.sidebar.title("ECHOLON")
st.sidebar.markdown("AI powered business intelligence")
st.sidebar.markdown("")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Upload Data", "Insights", "Predictions"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
if st.sidebar.button("Check Backend Connection"):
    try:
        res = requests.get(f"{BACKEND_API_URL}/health", timeout=5)
        if res.status_code == 200:
            st.sidebar.success("Backend is LIVE")
        else:
            st.sidebar.warning(f"Backend returned {res.status_code}")
    except Exception as e:
        st.sidebar.error(f"Could not connect")

# ================= HOME PAGE =============
if page == "Home":
    # Header
    st.markdown("# Welcome back")
    st.markdown("## Echolon AI Dashboard")
    
    # Top KPI Metrics - exactly like mockup
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Revenue Growth",
            value="+15.3%",
            delta="+15.3%"
        )
    
    with col2:
        st.metric(
            label="Customer Growth",
            value="+1.8%",
            delta="+1.8%"
        )
    
    with col3:
        st.metric(
            label="Acquisition Cost",
            value="$241K",
            delta="-10%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Churn Rate",
            value="2.3%",
            delta=None
        )
    
    st.markdown("")
    st.markdown("")
    
    # Charts Row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Revenue Overview")
        
        # Generate weekly data like in mockup
        weeks = ['Nov', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
        # Create more realistic wave pattern
        revenue_data = [8000, 12000, 10000, 15000, 18000, 16000, 22000, 19000, 24000, 20000]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weeks,
            y=revenue_data,
            mode='lines',
            name='Revenue',
            line=dict(color='#FFA500', width=3),  # Orange color like mockup
            fill=None
        ))
        
        fig.update_layout(
            xaxis_title="Weeks",
            yaxis_title="$30K",
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            plot_bgcolor='white',
            yaxis=dict(
                tickvals=[0, 10000, 20000, 30000],
                ticktext=['$0', '$10K', '$20K', '$30K'],
                gridcolor='#f0f0f0'
            ),
            xaxis=dict(
                gridcolor='#f0f0f0'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sales by Category")
        
        # Match mockup colors
        categories = ['SaaS', 'Support', 'Services', 'Other']
        values = [45, 25, 20, 10]
        colors = ['#4A90E2', '#7ED6D6', '#FFA07A', '#FFD700']
        
        fig2 = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=0.5,  # Donut chart
            marker_colors=colors,
            textinfo='percent',
            textfont_size=14
        )])
        
        fig2.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="right",
                x=1.3
            )
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("")
    st.markdown("")
    
    # Bottom sections - Insights and Predictions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Insights")
        st.markdown("""
        - Revenue growth has increased by 13.5% compared to the previous month.
        - Higher customer engagement correlates with lower churn rates.
        """)
    
    with col2:
        st.subheader("Predictions")
        st.markdown("""
        - Revenue is forecasted to increase by 7% in the next quarter.
        - Customer churn is expected to remain stable over the next months.
        """)
    
    with col3:
        st.subheader("Predictions")
        st.markdown("""
        - Revenue is forecasted to remain stable over the next months.
        """)

# ============= UPLOAD DATA PAGE =============
elif page == "Upload Data":
    st.markdown("# Upload Business Data")
    st.markdown("Upload your CSV file containing business data for analysis")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"File uploaded successfully! Shape: {df.shape[0]} rows x {df.shape[1]} columns")

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

            st.subheader("Column Information")
            col_info = pd.DataFrame({
                "Column Name": df.columns,
                "Data Type": df.dtypes.values,
                "Non-Null Count": df.count().values,
                "Null Count": df.isnull().sum().values
            })
            st.dataframe(col_info, use_container_width=True)

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
                            st.json(response.json())
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend: {str(e)}")
                        st.info("Make sure the backend service is running")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        st.info("Please upload a CSV file to begin")

# ============= INSIGHTS PAGE =============
elif page == "Insights":
    st.markdown("# Business Insights Dashboard")

    try:
        response = requests.get(f"{BACKEND_API_URL}/api/insights", timeout=10)
        if response.status_code == 200:
            insights_data = response.json()

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

            st.markdown("---")

            st.subheader("Trend Analysis")
            col1, col2 = st.columns(2)

            with col1:
                dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
                revenue = [180000 + i * 15000 + (i % 3) * 10000 for i in range(12)]
                fig = px.line(x=dates, y=revenue, title="Monthly Revenue Trend")
                fig.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                categories = ["Product A", "Product B", "Product C", "Product D"]
                values = [35, 28, 22, 15]
                fig = px.pie(values=values, names=categories, title="Revenue by Category")
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("Top Performing Segments")

            performance_data = pd.DataFrame({
                "Segment": ["Enterprise", "SMB", "Startup", "Individual"],
                "Revenue": ["$980K", "$720K", "$450K", "$250K"],
                "Growth": ["+15%", "+22%", "+8%", "+5%"],
                "Customers": [45, 180, 340, 1200]
            })
            st.dataframe(performance_data, use_container_width=True)
        else:
            st.warning("Could not fetch insights from backend")
            st.info("Displaying sample data for demonstration")
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        st.info("Make sure the backend service is running")

# ============= PREDICTIONS PAGE =============
elif page == "Predictions":
    st.markdown("# AI-Powered Predictions")
    st.markdown("Get intelligent forecasts and predictions for your business metrics")

    st.subheader("Prediction Configuration")
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

    if st.button("Generate Predictions", type="primary"):
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
                    st.success("Predictions generated successfully!")

                    st.subheader("Forecast Results")

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

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence Score", "87.5%")
                    with col2:
                        st.metric("Predicted Growth", "+18.2%")
                    with col3:
                        st.metric("Model Accuracy", "92.3%")
                else:
                    st.error(f"Prediction failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Backend service may be unavailable")

    st.markdown("---")
    st.info("Note: Predictions are generated using machine learning models trained on historical data. Accuracy improves with more data points and regular retraining.")

# Footer
st.markdown("---")
st.markdown("© 2024 Echolon AI | Built with Streamlit & FastAPI", unsafe_allow_html=True)
