import streamlit as st
# Trigger rebuild
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
# Import new utilities
from utils import DataValidator
from components import create_line_chart, create_bar_chart, COLORS, COLOR_PALETTE
from utils import create_multi_format_export, create_download_button
from utils import calculate_business_health_score, calculate_period_comparison
from components import display_business_health_score, display_metric_with_comparison, display_key_metrics_grid
# from ml_integration import get_ml_insights, initialize_ml_models, forecast_revenue_ml, detect_anomalies_ml, predict_churn_ml
from pages_financial_insights import render_financial_page
from pages_inventory_optimization import render_inventory_optimization_page
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

# ==================== SESSION STATE ====================
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
from pages_inventory_optimization import render_inventory_optimization_page
from pages_margin_analysis import render_margin_analysis_page
from pages_smart_alerts import render_smart_alerts_page
from pages_cohort_analysis import render_cohort_analysis_page
from pages_customer_ltv import render_customer_ltv_page
from pages_revenue_attribution import render_revenue_attribution_page
from pages_competitive_benchmark import render_competitive_benchmark_page


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

# ==================== SESSION STATE ====================
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
    else:
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
        'revenue': predictions
    })

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Echolon+AI", use_container_width=True)
    st.title("🎯 Echolon AI")
    st.markdown("### Business Intelligence Platform")
    357
    
    
    st.markdown("## 📍 Navigation")
    pages = {
        "🏠 Dashboard": "Dashboard",
        "📊 Analytics": "Analytics",
        "🔮 Predictions": "Predictions",
        "💡 Recommendations": "Recommendations",
        "📝 What-If Analysis": "What-If Analysis",
        "🎨 Inventory": "Inventory",
        "📂 Upload Data": "Upload Data",
    "👥 Customer Insights": "Customer Insights",
    "📊 Inventory & Demand": "Inventory & Demand",
    "⚠️ Anomalies & Alerts": "Anomalies & Alerts",
        "📂 Upload Data": "Data Sources",   "📋 Inventory Optimization": "Inventory Optimization",
         "📊 Margin Analysis": "Margin Analysis",
            "🔔 Smart Alerts": "Smart Alerts",
                "📊 Cohort Analysis": "Cohort Analysis",
                "💰 Customer LTV": "Customer LTV",
                "📈 Revenue Attribution": "Revenue Attribution",
                "🏆 Competitive Benchmark": "Competitive Benchmark",
    }
    
    for page_name, page_id in pages.items():
        if st.sidebar.button(page_name, key=page_id, use_container_width=True):
            st.session_state.current_page = page_id
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 Data Source")
    if st.session_state.uploaded_data is not None:
        st.info("✅ Using Uploaded Data")
    else:
        st.info("📋 Using Demo Data")
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ==================== LOAD DATA ====================
if st.session_state.uploaded_data is not None:
        data = st.session_state.uploaded_data
else:
    with st.spinner('Loading demo data...'):
        data = generate_demo_data()
    
# Initialize ML models
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

# ==================== PAGE: DASHBOARD ====================
if st.session_state.current_page == "Dashboard":
    st.title("🏠 Dashboard - CEO View")
    st.markdown("### High-level overview of your business at a glance")
        
    # Time Period Selector
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
    else:
        data_filtered = data
    
    # Recalculate KPIs for filtered period
    kpis = calculate_kpis(data_filtered)
    
    st.markdown("---")

        # ===================================================================================
    # SECTION 1: TOP-LEVEL KPI TILES
    # ===================================================================================
    
    # Calculate key metrics
    total_revenue = kpis.get('total_revenue', 0)
    revenue_per_day = total_revenue / 90 if total_revenue > 0 else 0
    revenue_growth = kpis.get('revenue_growth', 0)
    profit_margin = kpis.get('avg_profit_margin', 0)
    total_customers = int(kpis.get('total_customers', 0))
    total_orders = int(kpis.get('total_orders', 0))
    
    # Forecast revenue (mock: 5% growth)
    forecast_revenue = total_revenue * 1.05
    
    # Create 4 KPI columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Revenue (90d)",
            value=format_currency(total_revenue, decimals=0),
            delta=f"{revenue_growth:+.1f}% vs last period"
        )
    
    with col2:
        st.metric(
            label="📈 Profit Margin",
            value=f"{profit_margin:.1f}%",
            delta="+2.1% vs last month"
        )
    
    with col3:
        st.metric(
            label="👥 Active Customers",
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
        st.metric(
            label="📊 Avg Daily Revenue",
            value=format_currency(revenue_per_day, decimals=0),
            delta="+5.2% vs yesterday"
        )
    
    with col6:
        avg_order_value = kpis.get('avg_order_value', 0)
        st.metric(
            label="💳 Avg Order Value",
            value=format_currency(avg_order_value, decimals=2),
            delta="+3.1% vs last period"
        )
    
    with col7:
        st.metric(
            label="🔮 Forecast (30d)",
            value=format_currency(forecast_revenue / 3, decimals=0),
            delta="+5.0% projected"
        )
    
    with col8:
        # Inventory risk indicator (mock for now)
        st.metric(
            label="📦 Inventory Health",
            value="Good",
            delta="2 items low stock"
        )

        st.markdown("---")
    
    # ===================================================================================
    # SECTION 2: BUSINESS HEALTH SIGNAL
    # ===================================================================================

    # Business Health Score
    st.subheader("📊 Business Health Score")
    health_score_dict = calculate_business_health_score(kpis)
    display_business_health_score(health_score_dict)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
                pass  # Placeholder - KPI cards removed

            
    st.markdown("---")
    
    # ===================================================================================
    # SECTION 3: FORECAST SNAPSHOT
    # ===================================================================================
    
    st.subheader("📈 Revenue Forecast")
    st.caption("Future-facing projection for next 30 days")
    
    # Create forecast visualization
    forecast_col1, forecast_col2 = st.columns([2, 1])
    
    with forecast_col1:
        # Mock forecast data
        try:
            forecast_df = forecast_revenue(data, days_ahead=30)
            # Simple line chart
            fig = px.line(forecast_df, x='date', y='revenue', title="Revenue Projection")
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
        st.error(f"❌ Error generating forecast: {str(e)}")    
    with forecast_col2:
        st.metric(
            label="Projected Revenue (30d)",
                e=format_currency(forecast_revenue / 3, decimals=0),
            delta="+5.0% vs current pace"
        )
        st.caption("✅ At current pace, revenue is projected to grow 5% next month.")
    
    st.markdown("---")
    
    # ===================================================================================
    # SECTION 4: KEY INSIGHTS & ALERTS (The Brain of Echolon)
    # ===================================================================================
    
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
            "priority": "medium",
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
                priority_color = "red" if insight["priority"] == "high" else "orange" if insight["priority"] == "medium" else "green"
                st.markdown(f"**{insight['icon']} {insight['title']}**")
                st.caption(insight['description'])
                
            with col_insight2:
                if st.button("👁️ View", key=f"insight_{idx}"):
                    st.info(f"Action: {insight['action']}")
            
            if idx < len(insights):
                st.divider()
    
    st.markdown("---")
    
    # ===================================================================================
    # SECTION 5: RECOMMENDED ACTIONS
    # ===================================================================================
    
    st.subheader("✅ Recommended Actions")
    st.caption("AI-powered suggestions to improve your business")
    
    actions = [
        "📦 Reorder Product X by Friday to avoid stockout (9 days remaining)",
        "📊 Reduce ad spend on Campaign B (-15% conversion vs average)",
        "🎯 Focus promotions on weekdays (+18% performance vs weekends)"
    ]
    
    for idx, action in enumerate(actions, 1):
        st.info(f"**Action {idx}:** {action}")
    
    st.markdown("---")
    
    # ===================================================================================
    # SECTION 6: DATA FRESHNESS & STATUS
    # ===================================================================================
    
    current_time = datetime.now().strftime("%I:%M %p")
    st.caption(f"🔄 Last updated: {current_time} | Data sources: ✅ Connected | Status: Live")
    with col2:
                pass
    # REMOVED: Corrupted display_metric_with_comparison blocks that were causing TypeError        )
                
    # Row 2: Business Metrics
    
    with col5:
        # Customer Lifetime Value (CLV)
        clv = kpis.get('avg_order_value', 0) * 3  # Simplified: AOV * avg purchases
        st.metric("Customer Lifetime Value", format_currency(clv, decimals=0))
    
    with col6:
            # Customer Acquisition Cost (CAC)
        cac = (data['marketing_spend'].sum() / kpis.get('total_customers', 1)) if 'marketing_spend' in data.columns else 0
        st.metric("Customer Acquisition Cost", format_currency(cac, decimals=0))
    with col7:
        # Conversion data_filtered
        conv_rate = data['conversion_rate'].mean() if 'conversion_rate' in data_filtered.columns else 0
        st.metric("Avg Conversion Rate", format_percentage(conv_rate))
        st.markdown("---")    
    # Recent Activity & Trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        if 'revenue' in data.columns and 'date' in data.columns:
            fig = create_line_chart(data_filtered, 'date', ['revenue'], 'revenue', title='Last 90 Days Revenue', height=400)
            st.plotly_chart(fig, use_container_width=True) # Using standardized chart compone
        st.subheader("⚠️ Alerts & Notifications")

            
    # Row 3: Profitability Metrics
    col8, col9, col10 = st.columns(3)
    
    with col8:
        total_profit = kpis.get('total_profit', 0)
        st.metric("Total Profit", format_currency(total_profit, decimals=1))
    
    with col9:
        profit_margin = kpis.get('avg_profit_margin', 0)
        st.metric("Profit Margin", format_percentage(profit_margin))
    
    with col10:
        avg_roas = data['roas'].mean() if 'roas' in data.columns else 0
        st.metric("Avg ROAS", format_multiplier(avg_roas))
        # Smart alerts based on data
        alerts = []
        
        if kpis.get('revenue_growth', 0) < -10:
            alerts.append("🚨 **High Alert**: Revenue down {:.1f}%".format(abs(kpis.get('revenue_growth', 0))))
        elif kpis.get('revenue_growth', 0) > 20:
            alerts.append("⬆️ **Opportunity**: Revenue up {:.1f}%!".format(kpis.get('revenue_growth', 0)))
        
        if 'inventory_units' in data.columns:
            low_stock_days = (data['inventory_units'] < 600).sum()
            if low_stock_days > 5:
                alerts.append(f"📦 **Low Stock**: {low_stock_days} days with low inventory")
        
        if kpis.get('avg_order_value', 0) < 15:
            alerts.append("💸 **Margin Alert**: Profit margin below 15%")
        
        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("✅ All systems performing well!")
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔮 Run Forecast", use_container_width=True):
            st.session_state.current_page = "Predictions"
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()
    
    with col3:
        if st.button("💡 Get Recommendations", use_container_width=True):
            st.session_state.current_page = "Recommendations"
            st.rerun()
    
    with col4:
        if st.button("🎨 Check Inventory", use_container_width=True):
            st.session_state.current_page = "Inventory"
            st.rerun()

# ==================== PAGE: ANALYTICS ====================
elif st.session_state.current_page == "Analytics":
    st.title("📊 Analytics - Deep Dive")
    st.markdown("### Explore historical and real-time data insights")
    
    # Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_daily_rev = data['revenue'].mean() if 'revenue' in data.columns else 0
        st.metric("Avg Daily Revenue", format_currency(avg_daily_rev))    
    with col2:
        total_profit = kpis.get('total_profit', 0)
        st.metric("Total Profit", format_currency(total_profit, decimals=0))
    with col3:
        profit_margin = kpis.get('avg_profit_margin', 0)
        st.metric("Profit Margin", format_percentage(profit_margin))
    if 'roas' in data.columns:
        avg_roas = data['roas'].mean()
        st.metric("Avg ROAS", format_multiplier(avg_roas))
    st.markdown("---")
    st.subheader("💰 Sales Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Revenue Trends", "Distribution Analysis", "Correlation Matrix"])
    
    with tab1:
        if 'revenue' in data.columns and 'date' in data.columns:
            # Moving averages
            data_copy = data.copy()
            data_copy['MA7'] = data_copy['revenue'].rolling(window=7).mean()
            data_copy['MA30'] = data_copy['revenue'].rolling(window=30).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['revenue'], name='Actual', opacity=0.3))
            fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['MA7'], name='7-Day MA'))
            fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['MA30'], name='30-Day MA'))
            fig.update_layout(title='Revenue with Moving Averages', xaxis_title='Date', yaxis_title='Revenue ($)')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            if 'revenue' in data.columns:
                fig = px.histogram(data, x='revenue', nbins=30, title='Revenue Distribution')
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if 'orders' in data.columns:
                fig = px.histogram(data, x='orders', nbins=30, title='Orders Distribution')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        numeric_cols = ['revenue', 'orders', 'customers', 'profit', 'marketing_spend']
        available_cols = [col for col in numeric_cols if col in data.columns]
        if len(available_cols) >= 2:
            corr_matrix = data[available_cols].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title='Correlation Heatmap')
            st.plotly_chart(fig, use_container_width=True)
    
    # Customer Analytics
    st.markdown("---")
    st.subheader("👥 Customer Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        if 'customers' in data.columns and 'date' in data.columns:
            fig = px.line(data, x='date', y='customers', title='Customer Count Over Time')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'new_customers' in data.columns and 'date' in data.columns:
            fig = px.area(data.tail(90), x='date', y='new_customers', title='New Customers (Last 90 Days)')
            st.plotly_chart(fig, use_container_width=True)


    # Export Data Section
    st.markdown("---")
    st.subheader("📥 Export Analytics Data")
    create_multi_format_export(data, 'analytics_data', formats=['csv', 'excel', 'json'])
# ==================== PAGE: PREDICTIONS ====================
elif st.session_state.current_page == "Predictions":
    st.title("🔮 AI-Powered Predictions")

    st.markdown("### Forecast future performance using AI")
    
    # Forecast Controls
    col1, col2 = st.columns([3, 1])
    with col2:
        forecast_days = st.slider("Forecast Days Ahead", 7, 90, 30)
    
    # Revenue Forecast
    st.subheader("📈 Revenue Forecasting")
    forecast_df = forecast_revenue(data, days_ahead=forecast_days)
    
    if forecast_df is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['date'], y=data['revenue'], name='Historical', mode='lines', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['revenue'], name='Forecast', mode='lines', line=dict(color='red', dash='dash')))
        fig.update_layout(title=f'Revenue Forecast - Next {forecast_days} Days', xaxis_title='Date', yaxis_title='Revenue ($)')
        st.plotly_chart(fig, use_container_width=True)
    
        # Forecast Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            predicted_total = forecast_df['revenue'].sum()
            st.metric("Predicted Total Revenue", f"${predicted_total:,.0f}")
        with col2:
            predicted_avg = forecast_df['revenue'].mean()
            st.metric("Predicted Avg Daily Revenue", f"${predicted_avg:,.2f}")
        with col3:
            historical_avg = data['revenue'].tail(30).mean()
            change_pct = ((predicted_avg - historical_avg) / historical_avg) * 100
            st.metric("Expected Change", f"{change_pct:+.1f}%")
        
        # AI Confidence Score
        st.markdown("---")
        st.subheader("🎯 AI Confidence Score")
        confidence = max(50, min(95, 85 - abs(change_pct)))
        st.progress(confidence/100)
        st.write(f"**Confidence Level:** {confidence:.1f}%")
        
        if confidence > 80:
            st.success("✅ High confidence in predictions")
        elif confidence > 60:
            st.info("ℹ️ Moderate confidence - monitor trends")
        else:
            st.warning("⚠️ Lower confidence - high variability detected")

    # Export Data Section
    st.markdown("---")
    st.subheader("📥 Export Prediction Data")

    # Combine historical and forecast data for export
    if forecast_df is not None:
                forecast_df['data_type'] = 'forecast'
                historical_data = data.copy()
                historical_data['data_type'] = 'historical'
                combined_data = pd.concat([historical_data, forecast_df], ignore_index=True)
                create_multi_format_export(combined_data, 'predictions_data', formats=['csv', 'excel', 'json'])
    else:                        create_multi_format_export(data, 'predictions_data', formats=['csv', 'excel', 'json'])

# ==================== PAGE: RECOMMENDATIONS ====================
elif st.session_state.current_page == "Recommendations":
    st.title("💡 AI Business Recommendations")
    st.markdown("### Actionable insights derived from your data")
    
 # Get ML-powered insights
        # TODO: Implement get_ml_insights function
    ml_insights = {}  # Placehlder until function is implementedm
    
    # Generate Smart Recommendations
    recommendations = []
    
    # Revenue-based recommendations
    revenue_trend = kpis.get('revenue_growth', 0)
    if revenue_trend < -5:
        recommendations.append({
            'priority': 'High',
            'category': 'Revenue',
            'title': 'Address Declining Revenue',
            'action': f'Revenue declined by {abs(revenue_trend):.1f}%. Launch promotional campaign or review pricing strategy.',
            'impact': 'High',
            'effort': 'Medium'
        })
    elif revenue_trend > 15:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Growth',
            'title': 'Capitalize on Growth',
            'action': f'Revenue growing at {revenue_trend:.1f}%. Scale marketing and invest in customer retention programs.',
            'impact': 'High',
            'effort': 'Low'
        })
    
    # Inventory recommendations
    if 'inventory_units' in data.columns:
        avg_inventory = data['inventory_units'].mean()
        low_days = (data['inventory_units'] < avg_inventory * 0.5).sum()
        if low_days > 10:
            recommendations.append({
                'priority': 'High',
                'category': 'Inventory',
                'title': 'Optimize Stock Levels',
                'action': f'Detected {low_days} days with low inventory. Implement automated reordering at {avg_inventory*0.6:.0f} units.',
                'impact': 'Medium',
                'effort': 'Low',
            'annual_loss': avg_inventory * 12000,  # Estimated holding cost
            'immediate_impact': avg_inventory * 2000,  # Cash tied up
            'estimated_savings': avg_inventory * 6000,  # Annual savings from optimization
            })
    
    # Profit margin recommendations
    avg_margin = kpis.get('avg_order_value', 0)
    if avg_margin < 20:
        recommendations.append({
            'priority': 'High',
            'category': 'Profitability',
            'title': 'Improve Profit Margins',
            'action': f'Current margin is {avg_margin:.1f}%. Review supplier costs and consider 5-10% price increase on top products.',
            'impact': 'High',
            'effort': 'Medium',
            'annual_loss': total_profit * 0.20,  # Profit loss from poor margins
            'immediate_impact': total_profit * 0.15,  # Direct impact to this period
            'estimated_savings': (total_profit * 0.20) * 0.50,  # 50% improvement potential
        })
    
    # Marketing efficiency
    if 'roas' in data.columns:
        avg_roas = data['roas'].mean()
        if avg_roas < 2.5:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Marketing',
                'title': 'Optimize Marketing Spend',
                'action': f'ROAS is {avg_roas:.2f}x. Pause underperforming channels and reallocate budget to top performers.',
                'impact': 'Medium',
                'effort': 'Low'
            })
    
    # Display Recommendations
    st.subheader("🎯 Top Priority Actions")
    
    if recommendations:
        for idx, rec in enumerate(recommendations, 1):
            with st.expander(f"{idx}. [{rec['priority']} Priority] {rec['title']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Category:** {rec['category']}")
                with col2:
                    st.markdown(f"**Impact:** {rec['impact']}")
                with col3:
                    st.markdown(f"**Effort:** {rec['effort']}")
                st.markdown(f"**Action:** {rec['action']}")
            
            # Financial Impact Display
            if 'annual_loss' in rec:
                st.markdown(f"""\n**Financial Impact:**\n
💸 **You're losing:** {format_currency(rec['annual_loss'], 0)}/year\n
📊 **At immediate stake:** {format_currency(rec.get('immediate_impact', 0), 0)} in working capital\n
✅ **Expected savings:** {format_currency(rec.get('estimated_savings', 0), 0)} annually\n""")
            
            # Additional details
            st.markdown(f"**Status:** {rec['impact']} Impact | **Effort:** {rec['effort']} Effort")
    else:
        st.success("✅ Your business metrics are performing well!")

# ==================== PAGE: WHAT-IF ANALYSIS ====================
elif st.session_state.current_page == "What-If Analysis":
    st.title("📝 What-If Scenario Analysis")
    st.markdown("### Model strategic decisions without real-world risk")
    
    st.info("💡 Adjust variables below to see projected impact on your business")
    
    # Scenario Controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Revenue & Cost Assumptions")
        revenue_change = st.slider("Revenue Change (%)", -50, 100, 0, 5)
        cost_change = st.slider("Cost Change (%)", -50, 100, 0, 5)
    
    with col2:
        st.markdown("#### 📊 Marketing & Customers")
        marketing_change = st.slider("Marketing Spend Change (%)", -50, 100, 0, 5)
        customer_change = st.slider("Customer Growth (%)", -50, 100, 0, 5)
    
    # Calculate Scenarios
    base_revenue = data['revenue'].sum() if 'revenue' in data.columns else 0
    base_cost = data['cost'].sum() if 'cost' in data.columns else base_revenue * 0.6
    base_profit = base_revenue - base_cost
    base_margin = (base_profit / base_revenue * 100) if base_revenue > 0 else 0
    
    scenario_revenue = base_revenue * (1 + revenue_change/100)
    scenario_cost = base_cost * (1 + cost_change/100)
    scenario_profit = scenario_revenue - scenario_cost
    scenario_margin = (scenario_profit / scenario_revenue * 100) if scenario_revenue > 0 else 0
    
    st.markdown("---")
    st.subheader("📄 Scenario Results")
    
    # Comparison Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Revenue Change",
            format_currency(scenario_revenue - base_revenue, decimals=0)        )
    
    with col2:
        st.metric(
            "Total Profit Change",
            format_currency(scenario_profit - base_profit, decimals=0)        )
    
    with col3:
        st.metric(
        "Margin Change",            format_percentage(scenario_margin - base_margin)        )
    
    # Visualization
    st.markdown("---")
    st.subheader("📉 Base vs Scenario Comparison")
    
    comparison_df = pd.DataFrame({
        'Scenario': ['Base', 'What-If'],
        'Revenue': [base_revenue, scenario_revenue],
        'Cost': [base_cost, scenario_cost],
        'Profit': [base_profit, scenario_profit]
    })
    
    fig = go.Figure(data=[
        go.Bar(name='Revenue', x=comparison_df['Scenario'], y=comparison_df['Revenue']),
        go.Bar(name='Cost', x=comparison_df['Scenario'], y=comparison_df['Cost']),
        go.Bar(name='Profit', x=comparison_df['Scenario'], y=comparison_df['Profit'])
    ])
    fig.update_layout(barmode='group', title='Financial Impact Comparison')
    st.plotly_chart(fig, use_container_width=True)

    # Export Data Section
    st.markdown("---")
    st.subheader("📥 Export What-If Analysis Data")

    # Create export data with scenario comparison
    whatif_export = comparison_df.copy()
    whatif_export['revenue_change_%'] = revenue_change
    whatif_export['cost_change_%'] = cost_change
    whatif_export['marketing_change_%'] = marketing_change
    whatif_export['customer_change_%'] = customer_change
    create_multi_format_export(whatif_export, 'whatif_analysis', formats=['csv', 'excel', 'json'])

# ==================== PAGE: INVENTORY ====================
elif st.session_state.current_page == "Inventory":
    st.title("🎨 Inventory Management")
    st.markdown("### Centralized product and stock management")
    
    if 'inventory_units' not in data.columns:
        st.warning("⚠️ Inventory data not available. Upload data with 'inventory_units' column.")
    else:
        # Inventory KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        avg_inventory = data['inventory_units'].mean()
        max_inventory = data['inventory_units'].max()
        min_inventory = data['inventory_units'].min()
        inventory_vol = data['inventory_units'].std()
        
        with col1:
            st.metric("Avg Inventory Level", f"{format_number(avg_inventory)} units")
        with col2:
            st.metric("Peak Inventory", f"{format_number(max_inventory)} units")
        with col3:
            st.metric("Lowest Inventory", f"{format_number(min_inventory)} units")
        with col4:
            st.metric("Volatility", f"{format_number(inventory_vol)} units")        
        st.markdown("---")
        
        # Inventory Trend
        st.subheader("📈 Inventory Levels Over Time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['date'], y=data['inventory_units'], mode='lines', name='Inventory', fill='tozeroy'))
        fig.add_hline(y=avg_inventory, line_dash="dash", line_color="red", annotation_text="Average")
        fig.update_layout(title='Daily Inventory Levels', xaxis_title='Date', yaxis_title='Units')
        st.plotly_chart(fig, use_container_width=True)
        
        # Inventory Analytics
        st.markdown("---")
        st.subheader("🔄 Inventory Turnover Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_sales = data['orders'].sum() if 'orders' in data.columns else 0
            turnover_ratio = total_sales / avg_inventory if avg_inventory > 0 else 0
            st.metric("Inventory Turnover Ratio", f"{turnover_ratio:.2f}x")
            
            st.info("""
            **Interpretation:**
            - Higher ratio = faster inventory movement
            - Target: 5-10x per year
            - Too high: Risk of stockouts
            - Too low: Excess capital tied up
            """)
        
        with col2:
            days_inventory = 365 / turnover_ratio if turnover_ratio > 0 else 0
            st.metric("Days Inventory Outstanding", f"{days_inventory:.0f} days")
            
            st.info("""
            **Interpretation:**
            - Average days to sell inventory
            - Lower is generally better
            - Industry benchmarks vary
            - Monitor trends over time
            """)
        
        # AI-Powered Reorder Recommendations
        st.markdown("---")
        st.subheader("🤖 AI Reorder Recommendations")
        
        reorder_point = avg_inventory * 0.6
        optimal_stock = avg_inventory * 1.2
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Recommended Reorder Point", f"{reorder_point:.0f} units")
            st.write("Trigger reorders when inventory falls below this level")
        
        with col2:
            st.metric("Optimal Stock Level", f"{optimal_stock:.0f} units")
            st.write("Target inventory level to maintain")

# ==================== PAGE: UPLOAD DATA ====================
elif st.session_state.current_page == "Upload Data":
    st.title("📂 Upload Your Data")
    st.markdown("### Upload CSV to get personalized insights across all pages")

# ==================== PAGE: CUSTOMER INSIGHTS ====================
elif st.session_state.current_page == "Customer Insights":
    render_customer_insights_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: INVENTORY & DEMAND ====================
elif st.session_state.current_page == "Inventory & Demand":
    render_inventory_demand_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: ANOMALIES & ALERTS ====================
elif st.session_state.current_page == "Anomalies & Alerts":
    render_anomalies_alerts_page(data, kpis, format_currency, format_percentage, format_number)

    # ==================== PAGE: INVENTORY OPTIMIZATION ====================
elif st.session_state.current_page == "Inventory Optimization":
    render_inventory_optimization_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: MARGIN ANALYSIS ====================
elif st.session_state.current_page == "Margin Analysis":
    render_margin_analysis_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: SMART ALERTS ====================
elif st.session_state.current_page == "Smart Alerts":
    render_smart_alerts_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: COHORT ANALYSIS ====================
elif st.session_state.current_page == "Cohort Analysis":
    render_cohort_analysis_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: CUSTOMER LTV ====================
elif st.session_state.current_page == "Customer LTV":
    render_customer_ltv_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: REVENUE ATTRIBUTION ====================
elif st.session_state.current_page == "Revenue Attribution":
    render_revenue_attribution_page(data, kpis, format_currency, format_percentage, format_number)

# ==================== PAGE: COMPETITIVE BENCHMARK ====================
elif st.session_state.current_page == "Competitive Benchmark":
    render_competitive_benchmark_page(data, kpis, format_currency, format_percentage, format_number)
        
elif st.session_state.current_page == "Data Sources":    
        render_data_sources_page()
