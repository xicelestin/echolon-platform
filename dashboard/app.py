import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os
import io

# Page configuration - wide layout, no sidebar
st.set_page_config(
    page_title="Echolon AI - Business Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Custom CSS for modern UI matching the design
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Top navigation bar */
    .nav-bar {
        background-color: #1a1a2e;
        padding: 1rem 2rem;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .nav-logo {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        letter-spacing: 2px;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
    }
    
    .nav-link {
        color: #888;
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.3s;
    }
    
    .nav-link:hover, .nav-link.active {
        color: white;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    
    .metric-change {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    
    .metric-change.positive {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .metric-change.negative {
        background: #ffebee;
        color: #c62828;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        margin-bottom: 1rem;
    }
    
    /* Forecast panel */
    .forecast-panel {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        height: 100%;
    }
    
    .forecast-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    
    .forecast-highlight {
        color: #2e7d32;
        font-weight: 600;
    }
    
    /* Insight cards */
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        height: 100%;
    }
    
    .insight-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.75rem;
        font-size: 1rem;
    }
    
    .insight-icon.growth { background: #e8f5e9; }
    .insight-icon.alert { background: #fff3e0; }
    .insight-icon.advice { background: #fce4ec; }
    
    .insight-title {
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .insight-text {
        color: #666;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 1rem;
    }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Streamlit metric styling override */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
    
    /* Upload area styling */
    .uploadedFile {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'demo'
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None

# Navigation bar
nav_cols = st.columns([2, 6, 2])
with nav_cols[0]:
    st.markdown("### ECHOLON")
with nav_cols[1]:
    nav_options = st.columns(4)
    with nav_options[0]:
        if st.button("Home", use_container_width=True, type="secondary" if st.session_state.current_page != 'Home' else "primary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with nav_options[1]:
        if st.button("Upload Data", use_container_width=True, type="secondary" if st.session_state.current_page != 'Upload Data' else "primary"):
            st.session_state.current_page = 'Upload Data'
            st.rerun()
    with nav_options[2]:
        if st.button("Insights", use_container_width=True, type="secondary" if st.session_state.current_page != 'Insights' else "primary"):
            st.session_state.current_page = 'Insights'
            st.rerun()
    with nav_options[3]:
        if st.button("Predictions", use_container_width=True, type="secondary" if st.session_state.current_page != 'Predictions' else "primary"):
            st.session_state.current_page = 'Predictions'
            st.rerun()

st.markdown("---")

# ============= HOME PAGE =============
if st.session_state.current_page == "Home":
    
    # Top metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Revenue</div>
            <div class="metric-value">$24,700 <span class="metric-change positive">↑ 15%</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Bookings</div>
            <div class="metric-value">342 <span class="metric-change positive">↑ 7.9%</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Utilization</div>
            <div class="metric-value">86.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Revenue trend and Forecast panels
    chart_col, forecast_col = st.columns([2, 1])
    
    with chart_col:
        st.markdown('<div class="section-header">Revenue Trend</div>', unsafe_allow_html=True)
        
        # Generate trend data
        if st.session_state.uploaded_data is not None and 'date' in st.session_state.uploaded_data.columns:
            df = st.session_state.uploaded_data
            # Use first numeric column for chart
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if numeric_cols:
                chart_df = df[['date', numeric_cols[0]]].copy()
                chart_df.columns = ['Date', 'Value']
            else:
                chart_df = pd.DataFrame({
                    'Date': pd.date_range(start='2024-01-01', periods=6, freq='ME'),
                    'Value': [5000, 12000, 18000, 15000, 22000, 28000]
                })
        else:
            chart_df = pd.DataFrame({
                'Date': pd.date_range(start='2024-01-01', periods=6, freq='ME'),
                'Value': [5000, 12000, 18000, 15000, 22000, 28000]
            })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df['Date'],
            y=chart_df['Value'],
            mode='lines+markers',
            line=dict(color='#1a73e8', width=2),
            marker=dict(size=8, color='#1a73e8'),
            fill='tozeroy',
            fillcolor='rgba(26, 115, 232, 0.1)'
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=250,
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(showgrid=False, tickformat='%b'),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickprefix='$', tickformat=',')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with forecast_col:
        st.markdown('<div class="section-header">Upcoming Forecast</div>', unsafe_allow_html=True)
        
        # Calculate forecast from session data or use default
        forecast_pct = 14.4
        if st.session_state.forecast_data:
            points = st.session_state.forecast_data.get('points', [])
            if len(points) >= 2:
                first_val = points[0].get('value', 0)
                last_val = points[-1].get('value', 0)
                if first_val > 0:
                    forecast_pct = ((last_val - first_val) / first_val) * 100
        
        st.markdown(f"""
        <div class="forecast-panel">
            <p style="font-size: 1.1rem; line-height: 1.8;">
                A revenue increase of around <span class="forecast-highlight">{abs(forecast_pct):.1f}%</span> is <span class="forecast-highlight">expected</span> during the next 30 days.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Automated Insights section
    st.markdown('<div class="section-header">Automated Insights</div>', unsafe_allow_html=True)
    
    insight_cols = st.columns(3)
    
    with insight_cols[0]:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-icon growth">📈</div>
            <div class="insight-title">Growth Opportunity</div>
            <div class="insight-text">Customer acquisition has been steadily increasing over the past quarter.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_cols[1]:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-icon alert">⚠️</div>
            <div class="insight-title">Inventory Alert</div>
            <div class="insight-text">High demand for popular items may lead to stock shortages.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_cols[2]:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-icon advice">👥</div>
            <div class="insight-title">Staffing Advice</div>
            <div class="insight-text">Consider hiring additional staff to manage increasing bookings.</div>
        </div>
        """, unsafe_allow_html=True)

# ============= UPLOAD DATA PAGE =============
elif st.session_state.current_page == "Upload Data":
    st.markdown("## Upload Your Data")
    st.markdown("Upload a CSV file containing your business data for analysis")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Drag and drop your CSV file here",
            type="csv",
            help="Accepts any CSV with a date column and numeric metrics"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.uploaded_data = df
                st.session_state.data_source = 'uploaded'
                
                st.success(f"✅ File uploaded: {df.shape[0]} rows × {df.shape[1]} columns")
                
                st.markdown("### Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Summary metrics
                st.markdown("### Summary")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Total Rows", df.shape[0])
                with m2:
                    st.metric("Total Columns", df.shape[1])
                with m3:
                    st.metric("Missing Values", df.isnull().sum().sum())
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Save to backend button
                if st.button("💾 Process & Save to Backend", type="primary", use_container_width=True):
                    with st.spinner("Saving to backend..."):
                        try:
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                            response = requests.post(
                                f"{BACKEND_API_URL}/api/v1/upload_csv",
                                files=files,
                                timeout=30
                            )
                            if response.status_code == 200:
                                result = response.json()
                                st.success(f"✅ {result.get('message')} - {result.get('rows_processed')} rows processed")
                                st.balloons()
                            else:
                                error = response.json().get('detail', 'Unknown error')
                                st.error(f"Error: {error}")
                        except requests.exceptions.ConnectionError:
                            st.error("Could not connect to backend. Make sure it's running on port 8000.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with col2:
        st.markdown("### Accepted Formats")
        st.markdown("""
        Your CSV should include:
        - A **date** column
        - One or more **numeric metric** columns
        
        Example columns:
        - `date`, `revenue`, `bookings`
        - `date`, `sales`, `customers`, `orders`
        """)
        
        # Sample download
        sample_df = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'revenue': [50000 + i*500 + (i%7)*200 for i in range(30)],
            'bookings': [300 + i*5 + (i%5)*10 for i in range(30)],
            'utilization': [0.80 + i*0.005 for i in range(30)]
        })
        csv = sample_df.to_csv(index=False)
        st.download_button(
            "📥 Download Sample CSV",
            csv,
            "sample_business_data.csv",
            "text/csv",
            use_container_width=True
        )

# ============= INSIGHTS PAGE =============
elif st.session_state.current_page == "Insights":
    st.markdown("## Business Insights")
    
    # KPI cards
    kpi_cols = st.columns(4)
    kpis = [
        ("Total Revenue", "$2.4M", "+12.5%", True),
        ("Active Users", "8,432", "+8.2%", True),
        ("Conversion Rate", "3.8%", "+0.5%", True),
        ("Avg Order Value", "$285", "-2.1%", False)
    ]
    
    for col, (label, value, change, positive) in zip(kpi_cols, kpis):
        with col:
            change_class = "positive" if positive else "negative"
            arrow = "↑" if positive else "↓"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value} <span class="metric-change {change_class}">{arrow} {change}</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts row
    chart1, chart2 = st.columns(2)
    
    with chart1:
        st.markdown("### Revenue by Category")
        fig = px.pie(
            values=[45, 25, 20, 10],
            names=['Product A', 'Product B', 'Services', 'Other'],
            color_discrete_sequence=['#1a73e8', '#34a853', '#fbbc04', '#ea4335']
        )
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with chart2:
        st.markdown("### Monthly Trend")
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        values = [12000, 15000, 14000, 18000, 22000, 25000]
        fig = go.Figure(go.Bar(x=months, y=values, marker_color='#1a73e8'))
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

# ============= PREDICTIONS PAGE =============
elif st.session_state.current_page == "Predictions":
    st.markdown("## AI Predictions")
    st.markdown("Generate forecasts using machine learning models")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Configuration
    config_cols = st.columns(4)
    
    with config_cols[0]:
        metric_name = st.text_input("Metric Name", value="revenue", help="Name of the metric to forecast")
    with config_cols[1]:
        horizon = st.selectbox("Forecast Horizon", [7, 30, 60, 90], index=1, format_func=lambda x: f"{x} days")
    with config_cols[2]:
        model_type = st.selectbox("Model", ["auto", "xgboost", "prophet"])
    with config_cols[3]:
        business_id = st.number_input("Business ID", min_value=1, value=1)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Generate Forecast", type="primary", use_container_width=True):
        with st.spinner("Training model and generating forecast..."):
            try:
                response = requests.post(
                    f"{BACKEND_API_URL}/api/v1/ml/forecast",
                    json={
                        "business_id": business_id,
                        "metric_name": metric_name,
                        "horizon": horizon,
                        "model_type": model_type
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    forecast_data = response.json()
                    st.session_state.forecast_data = forecast_data
                    
                    st.success(f"✅ Forecast generated using {forecast_data.get('model_used', 'unknown')} model")
                    
                    points = forecast_data.get('points', [])
                    if points:
                        # Create forecast chart
                        dates = [p['date'] for p in points]
                        values = [p['value'] for p in points]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=dates, y=values,
                            mode='lines+markers',
                            line=dict(color='#1a73e8', width=2),
                            marker=dict(size=6)
                        ))
                        
                        # Add confidence intervals if available
                        lower = [p.get('lower_bound') for p in points]
                        upper = [p.get('upper_bound') for p in points]
                        if all(lower) and all(upper):
                            fig.add_trace(go.Scatter(
                                x=dates + dates[::-1],
                                y=upper + lower[::-1],
                                fill='toself',
                                fillcolor='rgba(26, 115, 232, 0.2)',
                                line=dict(color='rgba(255,255,255,0)'),
                                name='Confidence'
                            ))
                        
                        fig.update_layout(
                            title=f"{metric_name} Forecast - {horizon} Days",
                            margin=dict(l=0, r=0, t=40, b=0),
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Summary stats
                        st.markdown("### Forecast Summary")
                        s1, s2, s3 = st.columns(3)
                        with s1:
                            st.metric("Starting Value", f"${values[0]:,.0f}")
                        with s2:
                            st.metric("Ending Value", f"${values[-1]:,.0f}")
                        with s3:
                            growth = ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
                            st.metric("Projected Growth", f"{growth:+.1f}%")
                        
                        # Data table
                        with st.expander("View Forecast Data"):
                            st.dataframe(pd.DataFrame(points), use_container_width=True)
                
                elif response.status_code == 503:
                    st.error("ML services not available. Install XGBoost/Prophet.")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Make sure it's running.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.info("💡 Upload data first in the 'Upload Data' tab to generate forecasts based on your business metrics.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
    © 2024 Echolon AI | Powered by XGBoost & Prophet
</div>
""", unsafe_allow_html=True)
