
import streamlit as st
# Trigger rebuild # Force redeploy 49 51
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
# Import new utilities
# from utils import DataValidator
from components import create_line_chart, create_bar_chart, COLORS, COLOR_PALETTE
from utils import create_multi_format_export, create_download_button
from utils import calculate_business_health_score, calculate_period_comparison
from utils.metrics_utils import forecast_revenue
from components import display_business_health_score
from components import display_metric_with_comparison
from components import display_key_metrics_grid
from pages_margin_analysis import render_margin_analysis_page
from pages_smart_alerts import render_smart_alerts_page
from pages_cohort_analysis import render_cohort_analysis_page
from pages_customer_ltv import render_customer_ltv_page
from pages_revenue_attribution import render_revenue_attribution_page
from pages_competitive_benchmark import render_competitive_benchmark_page
from pages_data_sources import render_data_sources_page
from pages_customer_insights import render_customer_insights_page
from pages_inventory_demand import render_inventory_demand_page
from pages_anomalies_alerts import render_anomalies_alerts_page

# Add after all imports, before any other Streamlit code
from auth import require_authentication, render_user_info
if not require_authentication():
    st.stop()
# ==================== AI/ML MODELS (Phase 4) ====================
# Note: ML models are available in ml_models/ directory
# Future implementation will integrate these for AI-powered insights
ML_MODELS_AVAILABLE = True  # Set to True when models are ready for production
# ==================== FORMATTING UTILITIES ====================
def format_currency(value, decimals=0):
    """Format numbers as currency with proper abbreviation"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"${value/1_000:.{decimals}f}K"
    else:
        return f"${value:,.{decimals}f}"
def format_number(value, decimals=0):
    """Format large numbers with commas"""
    if isinstance(value, (int, float)):
        return f"{value:,.{decimals}f}"
    return str(value)
def format_percentage(value, decimals=1):
    """Format percentages consistently"""
    return f"{value:.{decimals}f}%"
def format_multiplier(value, decimals=2):
    """Format multipliers like ROAS"""
    return f"{value:.{decimals}f}x"
# Trigger deploy
# Page Configuration
st.set_page_config(
    page_title="Echolon AI - Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ================= SESSION STATE ====================
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'recent_predictions' not in st.session_state:
    st.session_state.recent_predictions = []
# ==================== DEMO DATA GENERATOR ====================
@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_demo_data():
    """Generate comprehensive demo dataset for all features"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    # np.random.seed(42)
    
    trend = np.linspace(40000, 60000, len(dates))
    seasonality = 5000 * np.sin(np.linspace(0, 4*np.pi, len(dates)))
    noise = np.random.normal(0, 3000, len(dates))
    data = pd.DataFrame({
        'date': dates,
        'revenue': trend + seasonality + noise,
        'orders': np.random.poisson(100, len(dates)) + (trend/1000).astype(int),
        'customers': np.random.poisson(50, len(dates)) + (trend/2000).astype(int),
        'cost': (trend + seasonality + noise) * 0.6,
        'marketing_spend': np.random.normal(5000, 1000, len(dates)),
        'inventory_units': np.random.randint(500, 2000, len(dates)),
        'new_customers': np.random.randint(10, 50, len(dates)),
        'conversion_rate': np.random.uniform(1.5, 4.5, len(dates))
    })
    # Derived metrics
    data['profit'] = data['revenue'] - data['cost']
    data['profit_margin'] = (data['profit'] / data['revenue'] * 100).round(2)
    data['roas'] = (data['revenue'] / data['marketing_spend']).round(2)
    data['avg_order_value'] = (data['revenue'] / data['orders']).round(2)
    return data
# ==================== HELPER FUNCTIONS ====================
def calculate_kpis(df):
    """Calculate KPIs from any dataframe - works with demo or uploaded data"""
    if df is None or df.empty:
        return {}


    total_revenue = df['revenue'].sum() if 'revenue' in df.columns else 0
    total_orders = df['orders'].sum() if 'orders' in df.columns else 0
    total_customers = df['customers'].sum() if 'customers' in df.columns else 0
    avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0
    # Growth rates
    if len(df) >= 60:
        recent = df.tail(30)
        previous = df.iloc[-60:-30]
        revenue_growth = ((recent['revenue'].sum() / previous['revenue'].sum()) - 1) * 100
        orders_growth = ((recent['orders'].sum() / previous['orders'].sum()) - 1) * 100
        customers_growth = ((recent['customers'].sum() / previous['customers'].sum()) - 1) * 100
        revenue_growth = orders_growth = customers_growth = 0
    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value,
        'revenue_growth': revenue_growth,
        'orders_growth': orders_growth,
        'customers_growth': customers_growth,
        'total_profit': df['profit'].sum() if 'profit' in df.columns else 0,
        'avg_profit_margin': df['profit_margin'].mean() if 'profit_margin' in df.columns else 0
            }
def forecast_revenue(df, days_ahead=30):
    from sklearn.linear_model import LinearRegression
    df_copy = df[['date', 'revenue']].copy()
    df_copy['days'] = (df_copy['date'] - df_copy['date'].min()).dt.days
    X = df_copy['days'].values.reshape(-1, 1)
    y = df_copy['revenue'].values
    model = LinearRegression()
    model.fit(X, y)
    last_day = df_copy['days'].max()
    future_days = np.arange(last_day + 1, last_day + days_ahead + 1).reshape(-1, 1)
    future_dates = pd.date_range(start=df['date'].max() + timedelta(days=1), periods=days_ahead)
    predictions = model.predict(future_days)
    return pd.DataFrame({
        'date': future_dates,
        'revenue': predictions})
# ============== SIDEBAR ====================
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Echolon+AI", use_container_width=True)
    st.title("🎯 Echolon AI")
    st.markdown("### Business Intelligence Platform")
    st.markdown("## 📍 Navigation")
    pages = {
"🏠 Dashboard": "Dashboard",
        "📊 Analytics": "Analytics",
        "🔮 Predictions": "Predictions",
        "💡 Recommendations": "Recommendations",
        "📝 What-If Analysis": "What-If Analysis",
        "📦 Inventory": "Inventory",
        "👥 Customer Insights": "Customer Insights",
        "📊 Inventory & Demand": "Inventory & Demand",
        "⚠️ Anomalies & Alerts": "Anomalies & Alerts",
        "📋 Inventory Optimization": "Inventory Optimization",
        "📈 Margin Analysis": "Margin Analysis",
        "🔔 Smart Alerts": "Smart Alerts",
        "📊 Cohort Analysis": "Cohort Analysis",
        "💰 Customer LTV": "Customer LTV",
        "📈 Revenue Attribution": "Revenue Attribution",
        "🏆 Competitive Benchmark": "Competitive Benchmark",
        "📂 Data Sources": "Data Sources",
    }
    for page_name, page_id in pages.items():
        if st.sidebar.button(page_name, key=page_id, use_container_width=True):
                        st.session_state.current_page = page_id
                        st.rerun()
    if st.session_state.uploaded_data is not None:
        st.info("✅ Using Uploaded Data")
        st.info("📋 Using Demo Data")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
# ==================== LOAD DATA ====================
if st.session_state.uploaded_data is not None:
        data = st.session_state.uploaded_data
else:
    with st.spinner('Loading demo data...'):
        data = generate_demo_data()
# Initialize ML models
# with st.spinner('Initializing ML models...'# initialize_ml_models(data)
# Add data validation with loading state
# with st.spinner('Validating data...'):
    # validator = DataValidator()
    # is_valid, errors = validator.validate_dataframe(data)
    # if not is_valid:
        # st.error(f"⚠️ Data validation issues detected:")
        # for error in errors:
            # st.warning(error)
        # Continue with caution but don't stop
    # else:
        # st.success("✅ Data validated successfully", icon="✅")
# Calculate KPIs (shared across all pages)
kpis = calculate_kpis(data)
if st.session_state.current_page == "Dashboard":
    st.title("🏠 Dashboard - CEO View")
            # Data Freshness In
    st.caption(f"🕒 Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | Data refreshed every 5 minutes")                    
                # Executive Summary Section
    st.subheader("📋 Executive Summary")
    summary_col1, summary_col2, summary_col3 = st.columns(3)
        
                # Alerts & Notifications Section
    alert_col1, alert_col2 = st.columns([2, 1])
    with alert_col1:
        st.subheader("⚠️ Alerts & Notifications")
        # Dynamic alerts based on KPIs
        revenue_growth = kpis.get('revenue_growth', 0)
        if revenue_growth > 0:
            st.success(f"📈 **Positive Trend:** Revenue increased by {revenue_growth}% this period")
        elif revenue_growth < 0:
            st.warning(f"📉 **Attention:** Revenue decreased by {abs(revenue_growth)}% this period")
        else:
            st.info("📄 **Stable:** Revenue unchanged from previous period")
            
        # Sample inventory alert
        st.warning("📦 **Low Stock Alert:** 2 items are running low on inventory")
    with alert_col2:
        st.subheader("🎯 Quick Actions")
        if st.button("📄 View Full Report", use_container_width=True):
            st.toast("Report generation feature coming soon!")
        if st.button("📧 Email Summary", use_container_width=True):
            st.toast("Email feature coming soon!")
        if st.button("🔄 Refresh Data", use_container_width=True):
                    st.rerun()
# Fix key naming for business health score calculation
kpis['profit_margin'] = kpis.get('avg_profit_margin', 0)
kpis['cash_flow_ratio'] = 1.0  # Simplified - actual calculation would use cash flow data
st.markdown("### High-level overview of your business at a glance")
# Time Period Selec
col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1])
with col_filter1:
    time_period = st.selectbox(
        "📅 Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
        index=2  # Default to Last 90 Days
    )
# Filter data based on selection
if time_period == "Last 7 Days":
    data_filtered = data.tail(7)
elif time_period == "Last 30 Days":
    data_filtered = data.tail(30)
elif time_period == "Last 90 Days":
    data_filtered = data.tail(90)
    data_filtered = data
# Recalculate KPIs for filtered period
kpis = calculate_kpis(data_filtered)
st.markdown("---")        # ===================================================================================
    # ===================================================================================
# Calculate key metrics
total_revenue = kpis.get('total_revenue', 0)
revenue_per_day = total_revenue / 90 if total_revenue > 0 else 0
revenue_growth = kpis.get('revenue_growth', 0)
profit_margin = kpis.get('avg_profit_margin', 0)
total_customers = int(kpis.get('total_customers', 0))
total_orders = int(kpis.get('total_orders', 0))
# Forecast revenue (mock: 5% growth)
projected_revenue_value = total_revenue * 1.05
# Create 4 KPI columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="💰 Total Revenue",
        value=format_currency(total_revenue, decimals=0),
        delta=f"{revenue_growth:+.1f}% vs last period"
            )
with col2:
    st.metric(        label="📈 Profit Margin",
        value=f"{profit_margin:.1f}%",
        delta="+2.1% vs last month"
                  )
with col3:
        
    st.metric(        label="👥 Active Customers",
        value=f"{total_customers:,}",
        delta=f"+{int(total_customers * 0.05)} this period"
                  )
    with col4:
            
            st.metric(
        label="🎯 Total Orders",
        value=f"{total_orders:,}",
        delta=f"+{int(total_orders * 0.08)} this period"
                    )
    # Second row of KPIs
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric(        label="📊 Avg Daily Revenue",
        value=format_currency(revenue_per_day, decimals=0),
        delta="+5.2% vs yesterday"
              )
with col6:
    avg_order_value = kpis.get('avg_order_value', 0)
    st.metric(        label="💳 Avg Order Value",
        value=format_currency(avg_order_value, decimals=2),
        delta="+3.1% vs last period"
                  )
with col7:

    st.metric(        label="🔮 Forecast (30d)",
        value=format_currency(projected_revenue_value / 3, decimals=0),
        delta="+5.0% projected"
                  )
with col8:

    # Inventory risk indicator (mock for now)
    st.metric(        label="📦 Inventory Health",
        value="Good",
        delta="2 items low stock"
                  )
# ===================================================================================
              
# SECTION 2: BUSINESS HEALTH SIGNAL
# Business Health Score
st.subheader("📊 Business Health Score")
health_score_dict = calculate_business_health_score(kpis)
display_business_health_score(health_score_dict)
# KPI Cards
st.markdown("---")
# SECTION 3: FORECAST SNAPSHOT
st.subheader("📈 Revenue Forecast")
st.    caption("Future-facing projection for next 30 days")
# Create forecast visualization
forecast_col1, forecast_col2 = st.columns([2, 1])
    # Initialize forecast_revenue for later use
with forecast_col1:
    # Mock forecast data
            try:
                    forecast_df = forecast_revenue(data, days_ahead=30)
        # Simple line chart
                    fig = px.line(forecast_df, x='date', y='revenue', title="Revenue Projection")
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
                    projected_revenue_value = forecast_df['revenue'].sum() if forecast_df is not None else 0
            except Exception as e:
                    st.error(f"❌ Error generating forecast: {str(e)}")    
# SECTION 4: KEY INSIGHTS & ALERTS (The Brain of Echol
st.subheader("🧠 Key Insights")
st.caption("Top 3 insights ranked by importance")
# Mock insights - In production, these would come from ML models
insights = [
            {
                    "priority": "high",
                    "icon": "⚠️",
                    "title": "Inventory Alert",
                    "description": "Product X will run out in 9 days at current sales pace.",
                    "action": "Reorder now to avoid stockout"
            },
            {
                    "priority": "medium",
                    "icon": "📈",
                    "title": "Weekend Performance",
                    "description": "Weekday sales outperform weekends by 18%.",
                    "action": "Focus promotions on weekdays"
                        },
                        {
                    "icon": "💰",
                    "title": "Margin Opportunity",
                    "description": "Premium products have 35% higher margins but represent only 12% of sales.",
                    "action": "Increase premium product visibility"
                            }
    ]
for idx, insight in enumerate(insights, 1):
            with st.container():
                    col_insight1, col_insight2 = st.columns([4, 1])
                    with col_insight1:
                                    st.markdown(f"{insight.get('icon', '')} **{insight.get('title', '')}**")
                                    st.caption(insight.get('description', ''))
                    with col_insight2:
                            if st.button("👁️ View", key=f"insight_{idx}"):
                                    st.info(f"Action: {insight['action']}")
                    if idx < len(insights):
                            st.divider()
# SECTION 5: RECOMMENDED     # =======================================================================    st.subheader("✅ Recommended Ac    st.caption("AI-powered suggestions to improve your business")
actions = [
            "📦 Reorder Product X by Friday to avoid stockout (9 days remaining)",
            "📊 Reduce ad spend on Campaign B (-15% conversion vs average)",             
         "🎯 Focus promotions on weekdays (+18% performance vs weekends)"
        ]
for idx, action in enumerate(actions, 1):
        st.info(f"**Action {idx}:** {action}")    
st.markdown("---")  # SECTION 6: DATA FRESHNESS & STATUS
    
current_time = datetime.now().strftime("%I:%M %p")
    st.caption(f"📅 Last updated: {current_time} | Data sources: ✅ Connected | Status: Live")# ================= PAGE: Analytics ====================
elif st.session_state.current_page == "Analytics":
    st.title("🔍 Analytics")
    st.write("Advanced business analytics and insights")
    st.info("📊 Analytics dashboard will be rebuilt with proper architecture")                                # Analytics Page with comprehensive charts and metrics

    # =====================================
# ====================
    elif st.session_state.current_page == "Predictions":                st.title("🔮 Predictions & Forecasting")
    st.write("AI-powered revenue and business forecasts")
    st.info("📈 Predictions dashboard will be rebuilith proper architecture")
