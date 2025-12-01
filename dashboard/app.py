import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import os
import io
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Echolon AI - Business Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'none'
if 'api_response' not in st.session_state:
    st.session_state.api_response = None


# ============= HELPER FUNCTIONS =============
def calculate_growth(series):
    if series is None or len(series) < 2:
        return None
    first_val = series.iloc[0]
    last_val = series.iloc[-1]
    if first_val == 0:
        return None
    return ((last_val - first_val) / first_val) * 100


def get_metric_summary(df, col_name):
    if col_name not in df.columns:
        return None
    series = df[col_name]
    return {
        'current': series.iloc[-1] if len(series) > 0 else 0,
        'average': series.mean(),
        'total': series.sum(),
        'growth': calculate_growth(series),
    }


def detect_numeric_columns(df):
    return df.select_dtypes(include=[np.number]).columns.tolist()


def generate_insights_from_data(df):
    insights = []
    numeric_cols = detect_numeric_columns(df)
    
    for col in numeric_cols:
        if col.lower() == 'date':
            continue
        summary = get_metric_summary(df, col)
        if summary and summary['growth'] is not None:
            direction = "increased" if summary['growth'] > 0 else "decreased"
            insights.append({
                'metric': col.title(),
                'insight': f"{col.title()} has {direction} by {abs(summary['growth']):.1f}%",
                'growth': summary['growth'],
                'type': 'growth'
            })
    
    if 'date' in df.columns:
        df_sorted = df.sort_values('date')
        for col in numeric_cols[:3]:
            if col.lower() == 'date':
                continue
            recent_avg = df_sorted[col].tail(len(df)//4).mean() if len(df) > 4 else df_sorted[col].mean()
            older_avg = df_sorted[col].head(len(df)//4).mean() if len(df) > 4 else df_sorted[col].mean()
            if older_avg > 0:
                trend_change = ((recent_avg - older_avg) / older_avg) * 100
                trend_direction = "upward" if trend_change > 0 else "downward"
                insights.append({
                    'metric': col.title(),
                    'insight': f"Recent {col.lower()} shows {trend_direction} trend ({trend_change:+.1f}%)",
                    'growth': trend_change,
                    'type': 'trend'
                })
    
    return insights


# ============= SIDEBAR =============
st.sidebar.title("ECHOLON")
st.sidebar.markdown("AI powered business intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", ["Home", "Upload Data", "Insights", "Predictions"])

st.sidebar.markdown("---")

if st.session_state.data_source == 'uploaded' and st.session_state.uploaded_data is not None:
    st.sidebar.success(f"✓ Data loaded: {len(st.session_state.uploaded_data)} rows")
else:
    st.sidebar.warning("No data uploaded")

st.sidebar.markdown("---")

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
    st.title("Echolon AI Dashboard")
    
    has_data = st.session_state.data_source == 'uploaded' and st.session_state.uploaded_data is not None
    
    if has_data:
        df = st.session_state.uploaded_data
        st.success("📊 Showing metrics from your uploaded data")
        st.markdown("---")
        
        numeric_cols = detect_numeric_columns(df)
        display_cols = [c for c in numeric_cols if c.lower() != 'date'][:4]
        
        st.subheader("Key Performance Indicators")
        
        if display_cols:
            cols = st.columns(len(display_cols))
            for i, col_name in enumerate(display_cols):
                with cols[i]:
                    summary = get_metric_summary(df, col_name)
                    if summary:
                        if summary['current'] > 10000:
                            display_val = f"${summary['current']/1000:.1f}K" if 'revenue' in col_name.lower() else f"{summary['current']/1000:.1f}K"
                        elif summary['current'] < 1:
                            display_val = f"{summary['current']*100:.1f}%"
                        else:
                            display_val = f"{summary['current']:,.0f}"
                        delta = f"{summary['growth']:+.1f}%" if summary['growth'] is not None else None
                        st.metric(label=col_name.replace('_', ' ').title(), value=display_val, delta=delta)
        else:
            st.warning("No numeric columns found")
        
        st.markdown("---")
        st.subheader("Data Trends")
        
        if 'date' in df.columns and len(display_cols) > 0:
            chart_metric = st.selectbox("Select metric", display_cols)
            chart_df = df[['date', chart_metric]].copy()
            chart_df['date'] = pd.to_datetime(chart_df['date'])
            chart_df = chart_df.sort_values('date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df[chart_metric], mode='lines+markers', name=chart_metric.title(), line=dict(color='#FF6B35', width=2)))
            fig.update_layout(title=f"{chart_metric.title()} Over Time", xaxis_title="Date", yaxis_title=chart_metric.title(), template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Auto-Generated Insights")
            insights = generate_insights_from_data(df)
            if insights:
                for insight in insights[:4]:
                    icon = "🔼" if insight['growth'] > 0 else "🔽"
                    st.markdown(f"{icon} **{insight['metric']}**: {insight['insight']}")
            else:
                st.info("Not enough data for insights")
        
        with col2:
            st.subheader("📊 Data Summary")
            st.markdown(f"**Total Records**: {len(df):,}")
            if 'date' in df.columns:
                st.markdown(f"**Date Range**: {df['date'].min()} to {df['date'].max()}")
            st.markdown(f"**Metrics**: {', '.join(display_cols)}")
    
    else:
        st.info("👋 Welcome! Upload your business data to get started.")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 📤 Upload Data")
            st.markdown("Upload CSV with `date`, `revenue`, `customers`")
        with col2:
            st.markdown("### 🔮 Get Predictions")
            st.markdown("ML models forecast your metrics")
        with col3:
            st.markdown("### 📊 Discover Insights")
            st.markdown("Auto-detect patterns and trends")
        
        st.markdown("---")
        st.subheader("Sample Data Format")
        sample_df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'revenue': [50000, 52000, 51500],
            'customers': [245, 248, 250]
        })
        st.dataframe(sample_df, use_container_width=True)


# ============= UPLOAD DATA PAGE =============
elif page == "Upload Data":
    st.title("Upload Your Data")
    st.markdown("---")
    
    sample_data = pd.DataFrame({'date': ['2024-01-01', '2024-01-02'], 'revenue': [50000, 52000], 'customers': [245, 248]})
    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    st.download_button(label="Download sample CSV", data=csv_buffer.getvalue(), file_name="sample_data.csv", mime="text/csv")
    
    st.markdown("---")
    
    # Show currently loaded data if exists
    if st.session_state.uploaded_data is not None:
        st.success(f"✅ Data already loaded: {len(st.session_state.uploaded_data)} rows × {len(st.session_state.uploaded_data.columns)} columns")
        st.dataframe(st.session_state.uploaded_data.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(st.session_state.uploaded_data))
        with col2:
            st.metric("Columns", len(st.session_state.uploaded_data.columns))
        with col3:
            st.metric("Missing", st.session_state.uploaded_data.isnull().sum().sum())
        
        numeric_cols = detect_numeric_columns(st.session_state.uploaded_data)
        if numeric_cols:
            st.info(f"📊 Metrics: {', '.join(numeric_cols)}")
        
        st.markdown("---")
        st.markdown("**Upload a new file to replace current data:**")
    
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_data = df
            st.session_state.data_source = 'uploaded'
            
            st.success(f"New file: {df.shape[0]} rows × {df.shape[1]} columns")
            st.dataframe(df.head(10), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                st.metric("Missing", df.isnull().sum().sum())
            
            numeric_cols = detect_numeric_columns(df)
            if numeric_cols:
                st.info(f"📊 Detected: {', '.join(numeric_cols)}")
            
            if st.button("Process & Save to Backend", type="primary"):
                with st.spinner("Processing..."):
                    try:
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                        response = requests.post(f"{BACKEND_API_URL}/api/v1/upload_csv", files=files, timeout=30)
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Saved! ({result.get('rows_processed', 0)} rows)")
                            st.session_state.data_saved = True
                            st.balloons()
                        else:
                            try:
                                st.error(f"Error: {response.json().get('detail', response.text)}")
                            except:
                                st.error(f"Error: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Backend not connected")
                    except Exception as e:
                        st.error(f"Failed: {str(e)}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    elif st.session_state.uploaded_data is None:
        st.info("Upload a CSV file to begin")


# ============= INSIGHTS PAGE =============
elif page == "Insights":
    st.title("Business Insights")
    
    has_data = st.session_state.data_source == 'uploaded' and st.session_state.uploaded_data is not None
    
    if has_data:
        df = st.session_state.uploaded_data
        st.success("📊 Insights from your data")
        st.markdown("---")
        
        numeric_cols = detect_numeric_columns(df)
        display_cols = [c for c in numeric_cols if c.lower() != 'date'][:4]
        
        if display_cols:
            cols = st.columns(len(display_cols))
            for i, col_name in enumerate(display_cols):
                with cols[i]:
                    summary = get_metric_summary(df, col_name)
                    if summary:
                        if summary['total'] > 100000:
                            display_val = f"${summary['total']/1000000:.2f}M" if 'revenue' in col_name.lower() else f"{summary['total']/1000:.1f}K"
                        else:
                            display_val = f"{summary['current']:,.0f}"
                        delta = f"{summary['growth']:+.1f}%" if summary['growth'] else None
                        st.metric(col_name.title(), display_val, delta)
        
        st.markdown("---")
        st.subheader("🤖 AI Insights")
        insights = generate_insights_from_data(df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Growth Analysis")
            for i in [x for x in insights if x['type'] == 'growth']:
                icon = "🔼" if i['growth'] > 0 else "🔽"
                st.markdown(f"{icon} {i['insight']}")
        with col2:
            st.markdown("#### Trend Analysis")
            for i in [x for x in insights if x['type'] == 'trend']:
                icon = "📈" if i['growth'] > 0 else "📉"
                st.markdown(f"{icon} {i['insight']}")
        
        if len(display_cols) >= 2:
            st.markdown("---")
            st.subheader("📊 Correlations")
            fig = px.imshow(df[display_cols].corr(), text_auto=True, color_continuous_scale='RdBu_r')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No data uploaded")
        st.markdown("Upload data to see insights. Go to **Upload Data** page.")


# ============= PREDICTIONS PAGE =============
elif page == "Predictions":
    st.title("AI Predictions")
    
    has_data = st.session_state.data_source == 'uploaded' and st.session_state.uploaded_data is not None
    
    if not has_data:
        st.warning("⚠️ Upload data first")
        st.info("Go to **Upload Data** and save to backend.")
    else:
        df = st.session_state.uploaded_data
        numeric_cols = [c for c in detect_numeric_columns(df) if c.lower() != 'date']
        
        st.subheader("🎯 Configuration")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            metric_to_predict = st.selectbox("Metric", numeric_cols) if numeric_cols else st.text_input("Metric", "revenue")
        with col2:
            horizon_days = st.selectbox("Horizon", [7, 30, 90, 180, 365], format_func=lambda x: f"{x} Days", index=1)
        with col3:
            model_type = st.selectbox("Model", ["auto", "xgboost", "prophet"])
        
        business_id = st.number_input("Business ID", min_value=1, value=1)
        
        if st.button("🚀 Generate Forecast", type="primary"):
            with st.spinner("Training..."):
                try:
                    response = requests.post(
                        f"{BACKEND_API_URL}/api/v1/ml/forecast",
                        json={"business_id": int(business_id), "metric_name": metric_to_predict, "horizon": horizon_days, "model_type": model_type},
                        timeout=120
                    )
                    if response.status_code == 200:
                        forecast_data = response.json()
                        st.success(f"✅ Generated with {forecast_data.get('model_used', 'unknown')}!")
                        
                        points = forecast_data.get('points', [])
                        if points:
                            forecast_dates = [pd.to_datetime(p['date']) for p in points]
                            forecast_values = [p['value'] for p in points]
                            
                            fig = go.Figure()
                            
                            if 'date' in df.columns and metric_to_predict in df.columns:
                                hist_df = df[['date', metric_to_predict]].copy()
                                hist_df['date'] = pd.to_datetime(hist_df['date'])
                                fig.add_trace(go.Scatter(x=hist_df['date'], y=hist_df[metric_to_predict], name="Historical", line=dict(color="blue")))
                            
                            fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_values, name="Forecast", line=dict(color="orange", dash='dash')))
                            fig.update_layout(title=f"{metric_to_predict.title()} Forecast", template="plotly_white")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            metrics = forecast_data.get('metrics')
                            if metrics:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("MAE", f"{metrics.get('mae', 0):.2f}")
                                with col2:
                                    st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
                                with col3:
                                    st.metric("Samples", metrics.get('train_samples', 0))
                            
                            avg_val = sum(forecast_values) / len(forecast_values)
                            growth = ((forecast_values[-1] - forecast_values[0]) / forecast_values[0] * 100) if forecast_values[0] > 0 else 0
                            st.info(f"📈 Average: {avg_val:,.2f} | Growth: {growth:+.2f}%")
                    else:
                        try:
                            error_msg = response.json().get('detail', response.text)
                        except:
                            error_msg = response.text or f"HTTP {response.status_code}"
                        st.error(f"Error: {error_msg}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Backend not connected. Start the backend server first.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Try again or use a smaller dataset.")
                except Exception as e:
                    st.error(f"❌ {str(e)}")


st.markdown("---")
st.markdown("© 2024 Echolon AI")
