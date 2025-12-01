import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import os
import io

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

# Sidebar navigation - NO EMOJIS
st.sidebar.title("ECHOLON")
st.sidebar.markdown("AI powered business intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Upload Data", "Insights", "Predictions"]
)

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

# ============= UPLOAD DATA PAGE =============
elif page == "Upload Data":
    st.title("Upload Your Data")
    st.markdown("Upload a CSV file containing your business data for analysis and AI-powered insights")
    
    st.markdown("---")
    
    # Sample CSV download
    st.subheader("Sample CSV Format")
    sample_data = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'revenue': [50000, 52000, 51500],
        'customers': [245, 248, 250],
        'churn_rate': [2.1, 2.0, 2.2]
    })
    
    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    
    st.download_button(
        label="Download sample CSV",
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
                            f"{BACKEND_API_URL}/api/v1/upload_csv",
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
        response = requests.get(f"{BACKEND_API_URL}/api/v1/insights", timeout=10)
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
    
    st.subheader("🎯 Prediction Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_to_predict = st.text_input(
            "Metric Name",
            value="Revenue",
            help="Enter the exact metric name from your uploaded data"
        )
    with col2:
        horizon_days = st.selectbox(
            "Prediction Horizon",
            [7, 30, 90, 180, 365],
            format_func=lambda x: f"{x} Days",
            index=1
        )
    
    with col3:
        model_type = st.selectbox(
            "Model Type",
            ["auto", "xgboost", "prophet"],
            help="'auto' will choose the best available model"
        )
    
    business_id = st.number_input(
        "Business ID",
        min_value=1,
        value=1,
        help="Your business/user ID (default: 1)"
    )
    
    if st.button("🚀 Generate Forecast", type="primary"):
        with st.spinner("Training model and generating forecast..."):
            try:
                # Call the ML forecast endpoint
                response = requests.post(
                    f"{BACKEND_API_URL}/api/v1/ml/forecast",
                    json={
                        "business_id": int(business_id),
                        "metric_name": metric_to_predict,
                        "horizon": horizon_days,
                        "model_type": model_type
                    },
                    timeout=120  # Longer timeout for model training
                )
                if response.status_code == 200:
                    forecast_data = response.json()
                    
                    st.success(f"✅ Forecast generated successfully using {forecast_data.get('model_used', 'unknown')} model!")
                    
                    # Display forecast results
                    st.subheader("📈 Forecast Results")
                    
                    # Extract forecast points
                    points = forecast_data.get('points', [])
                    if not points:
                        st.warning("No forecast points returned")
                    else:
                        # Prepare data for visualization
                        forecast_dates = [pd.to_datetime(p['date']) for p in points]
                        forecast_values = [p['value'] for p in points]
                        lower_bounds = [p.get('lower_bound') for p in points if p.get('lower_bound')]
                        upper_bounds = [p.get('upper_bound') for p in points if p.get('upper_bound')]
                        
                        # Create visualization
                        fig = go.Figure()
                        
                        # Add forecast line
                        fig.add_trace(go.Scatter(
                            x=forecast_dates,
                            y=forecast_values,
                            name="Forecast",
                            mode="lines+markers",
                            line=dict(color="orange", width=2),
                            marker=dict(size=6)
                        ))
                        
                        # Add confidence intervals if available (Prophet)
                        if lower_bounds and upper_bounds and len(lower_bounds) == len(forecast_dates):
                            fig.add_trace(go.Scatter(
                                x=forecast_dates,
                                y=upper_bounds,
                                name="Upper Bound",
                                mode="lines",
                                line=dict(width=0),
                                showlegend=False
                            ))
                            fig.add_trace(go.Scatter(
                                x=forecast_dates,
                                y=lower_bounds,
                                name="Confidence Interval",
                                mode="lines",
                                line=dict(width=0),
                                fill="tonexty",
                                fillcolor="rgba(255,165,0,0.2)",
                                showlegend=True
                            ))
                        
                        fig.update_layout(
                            title=f"{metric_to_predict} Forecast - {horizon_days} Days",
                            xaxis_title="Date",
                            yaxis_title=metric_to_predict,
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display model metrics if available
                        model_metrics = forecast_data.get('metrics')
                        if model_metrics:
                            st.subheader("📊 Model Performance")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if 'mae' in model_metrics:
                                    st.metric("Mean Absolute Error", f"{model_metrics['mae']:.2f}")
                            with col2:
                                if 'rmse' in model_metrics:
                                    st.metric("Root Mean Squared Error", f"{model_metrics['rmse']:.2f}")
                            with col3:
                                if 'train_samples' in model_metrics:
                                    st.metric("Training Samples", model_metrics['train_samples'])
                        
                        # Display forecast summary
                        st.subheader("📋 Forecast Summary")
                        if forecast_values:
                            avg_forecast = sum(forecast_values) / len(forecast_values)
                            first_value = forecast_values[0]
                            last_value = forecast_values[-1]
                            growth = ((last_value - first_value) / first_value * 100) if first_value > 0 else 0
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Average Forecast", f"{avg_forecast:,.2f}")
                            with col2:
                                st.metric("Starting Value", f"{first_value:,.2f}")
                            with col3:
                                st.metric("Ending Value", f"{last_value:,.2f}")
                            
                            if growth != 0:
                                st.info(f"📈 Projected {'growth' if growth > 0 else 'decline'}: {growth:+.2f}% over {horizon_days} days")
                        
                        # Show data table
                        with st.expander("📄 View Forecast Data Table"):
                            forecast_df = pd.DataFrame(points)
                            st.dataframe(forecast_df, use_container_width=True)
                    
                elif response.status_code == 503:
                    st.error("❌ ML services not available. Please install required dependencies (XGBoost/Prophet).")
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"❌ Forecast failed: {error_detail}")
                    st.json(response.json())
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Model training may take longer. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to backend. Make sure the backend is running on port 8000.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure you have uploaded data first using the 'Upload Data' page")
    
    st.markdown("---")
    st.info("💡 **Note**: Predictions are generated using machine learning models trained on historical data. Accuracy improves with more data points and regular retraining.")

# Footer
st.markdown("---")
st.markdown("""
© 2024 Echolon AI | Built with Streamlit & FastAPI
""")
