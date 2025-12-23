import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ==================== AI/ML MODELS INTEGRATION ====================
try:
    from ml_models.revenue_forecaster import RevenueForecaster
    from ml_models.anomaly_detection import AnomalyDetector
    from ml_models.churn_prediction import ChurnPredictor
    from ml_models.demand_forecasting import DemandForecaster
    ML_MODELS_AVAILABLE = True
except ImportError:
    ML_MODELS_AVAILABLE = False
    st.warning("⚠️ ML Models not available - using rule-based insights only")


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
    st.markdown("---")
    
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
    "⚠️ Anomalies & Alerts": "Anomalies & Alerts"
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
    data = generate_demo_data()

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
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Revenue",
                format_currency(kpis.get('total_revenue', 0), decimals=1),            f"{kpis.get('revenue_growth', 0):.1f}%"
        )
    with col2:
        st.metric(
            "Total Orders",
            f"{format_number(kpis.get('total_orders', 0))}",
        )
            
    with col3:
        st.metric(
            "Total Customers",
            f"{format_number(kpis.get('total_customers', 0))}",
            f"{format_percentage(kpis.get('customers_growth', 0))}")
    
    with col4:
        st.metric(
            "Avg Order Value",
            f"{format_currency(kpis.get('avg_order_value', 0), decimals=0)}"
        )

                
    # Row 2: Business Metrics
    col5, col6, col7 = st.columns(3)
    
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
            fig = px.line(data_filtered, x='date', y=
            'revenue', title='Last 90 Days Revenue')
            fig.update_layout(xaxis_title='Date', yaxis_title='Revenue ($)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
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

# ==================== PAGE: RECOMMENDATIONS ====================
elif st.session_state.current_page == "Recommendations":
    st.title("💡 AI Business Recommendations")
    st.markdown("### Actionable insights derived from your data")
    
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
                'effort': 'Low'
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
            'effort': 'Medium'
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
        
    st.info("""
    📊 **Upload your business data to unlock personalized insights!**
    
    Your CSV should include these columns:
    - `date` - Transaction date
    - `revenue` - Revenue amount
    - `orders` - Number of orders
    - `customers` - Number of customers
    
    💡 After uploading, all dashboards will automatically update with your data!
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate
            required_cols = ['date', 'revenue', 'orders', 'customers']
            missing_cols = [col for col in required_cols if col not in df.columns.str.lower()]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                st.info("📄 Required columns: date, revenue, orders, customers")
            else:
                df.columns = df.columns.str.lower()
                
                # Validate data types
                errors = []
                try:
                    df['date'] = pd.to_datetime(df['date'])
                except:
                    errors.append("📅 Date column must be valid date format")
                
                for col in ['revenue', 'orders', 'customers']:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='raise')
                        if (df[col] < 0).any():
                            errors.append(f"⚠️ {col.capitalize()} contains negative values")
                    except:
                        errors.append(f"🔢 {col.capitalize()} must contain numbers")
                
                if errors:
                    st.error("**Validation Failed:**")
                    for error in errors:
                        st.markdown(f"- {error}")
                else:
                    # Add derived metrics
                    if 'cost' in df.columns and 'profit' not in df.columns:
                        df['profit'] = df['revenue'] - df['cost']
                        df['profit_margin'] = (df['profit'] / df['revenue'] * 100).round(2)
                    
                    if 'marketing_spend' in df.columns and 'roas' not in df.columns:
                        df['roas'] = (df['revenue'] / df['marketing_spend']).round(2)
                    
                    # Show preview
                    st.success(f"✅ Successfully loaded {len(df)} rows!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Rows", len(df))
                    with col2:
                        date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
                        st.metric("Date Range", date_range)
                    with col3:
                        quality = int((1 - df.isnull().sum().sum()/(len(df)*len(df.columns))) * 100)
                        st.metric("Data Quality", f"{quality}%")
                    
                    st.dataframe(df.head(10), use_container_width=True)
                
                if st.button("Use This Data", type="primary", use_container_width=True):
                    st.session_state.uploaded_data = df
                    st.success("Data uploaded successfully!")
                    st.rerun()    
        except Exception as e:
            st.error(f"Upload error: {str(e)}")  
    
    # Data Management
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.uploaded_data is not None:
            st.info("✅ Currently using uploaded data")
        else:
            st.info("📋 Currently using demo data")
    
    with col2:
        if st.button("🔄 Reset to Demo Data", type="secondary", use_container_width=True):
            st.session_state.uploaded_data = None
            st.success("✅ Reset to demo data!")
            st.rerun()
