import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from scipy import stats
from sklearn.linear_model import LinearRegression

# Page config
st.set_page_config(
    page_title="Echolon AI - Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Sample data generator for demo
def generate_demo_data():
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    # Generate base trend
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
        'inventory_units': np.random.randint(500, 2000, len(dates))
    })
    
    data['profit'] = data['revenue'] - data['cost']
    data['profit_margin'] = (data['profit'] / data['revenue'] * 100).round(2)
    data['conversion_rate'] = (data['customers'] / (data['customers'] * 3) * 100).round(2)
    data['roas'] = (data['revenue'] / data['marketing_spend']).round(2)
    
    return data

# KPI Calculator
def calculate_kpis(df):
    if df is None or df.empty:
        return {}
    
    total_revenue = df['revenue'].sum()
    total_orders = df['orders'].sum()
    total_customers = df['customers'].sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_profit = df['profit'].sum() if 'profit' in df.columns else 0
    avg_profit_margin = df['profit_margin'].mean() if 'profit_margin' in df.columns else 0
    
    # Calculate growth rates (last 30 days vs previous 30 days)
    if len(df) >= 60:
        recent = df.tail(30)
        previous = df.iloc[-60:-30]
        
        revenue_growth = ((recent['revenue'].sum() / previous['revenue'].sum()) - 1) * 100
        orders_growth = ((recent['orders'].sum() / previous['orders'].sum()) - 1) * 100
        customers_growth = ((recent['customers'].sum() / previous['customers'].sum()) - 1) * 100
    else:
        revenue_growth = 0
        orders_growth = 0
        customers_growth = 0
    
    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value,
        'total_profit': total_profit,
        'avg_profit_margin': avg_profit_margin,
        'revenue_growth': revenue_growth,
        'orders_growth': orders_growth,
        'customers_growth': customers_growth
    }

# Reusable KPI Rendering Function
def render_kpi_strip(kpis_dict, benchmark_config=None, num_columns=4):
    """
    Renders a reusable KPI strip that accepts a data slice and benchmark config.
    
    Args:
        kpis_dict: Dictionary containing KPI values from calculate_kpis()
        benchmark_config: Optional dict with benchmark values for comparison
        num_columns: Number of columns to display (default: 4)
    
    Returns:
        None (renders Streamlit UI components)
    """
    if not kpis_dict:
        st.warning("No KPI data available")
        return
    
    # Default KPI configuration
    kpi_config = [
        {
            'label': 'Total Revenue',
            'key': 'total_revenue',
            'format': 'currency',
            'delta_key': 'revenue_growth'
        },
        {
            'label': 'Total Orders',
            'key': 'total_orders',
            'format': 'number',
            'delta_key': 'orders_growth'
        },
        {
            'label': 'Total Customers',
            'key': 'total_customers',
            'format': 'number',
            'delta_key': 'customers_growth'
        },
        {
            'label': 'Avg Order Value',
            'key': 'avg_order_value',
            'format': 'currency_decimal',
            'delta_suffix': ' margin',
            'delta_key': 'avg_profit_margin'
        }
    ]
    
    # Apply benchmark config if provided
    if benchmark_config:
        kpi_config = benchmark_config
    
    # Create columns
    cols = st.columns(num_columns)
    
    # Render each KPI
    for idx, kpi in enumerate(kpi_config[:num_columns]):
        with cols[idx]:
            # Get value
            value = kpis_dict.get(kpi['key'], 0)
            
            # Format value based on type
            if kpi['format'] == 'currency':
                formatted_value = f"${value:,.0f}"
            elif kpi['format'] == 'currency_decimal':
                formatted_value = f"${value:.2f}"
            elif kpi['format'] == 'number':
                formatted_value = f"{value:,.0f}"
            elif kpi['format'] == 'percentage':
                formatted_value = f"{value:.1f}%"
            else:
                formatted_value = str(value)
            
            # Get delta value if available
            delta = None
            if 'delta_key' in kpi:
                delta_value = kpis_dict.get(kpi['delta_key'], 0)
                delta_suffix = kpi.get('delta_suffix', '')
                delta = f"{delta_value:.1f}%{delta_suffix}"
            
            # Render metric
            st.metric(
                label=kpi['label'],
                value=formatted_value,
                delta=delta
            )



# Forecasting function
def forecast_metric(df, metric, days_ahead=30):
    if len(df) < 30:
        return None
    
    # Prepare data
    df_metric = df[['date', metric]].copy()
    df_metric['days'] = (df_metric['date'] - df_metric['date'].min()).dt.days
    
    X = df_metric['days'].values.reshape(-1, 1)
    y = df_metric[metric].values
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future dates
    last_day = df_metric['days'].max()
    future_days = np.arange(last_day + 1, last_day + days_ahead + 1).reshape(-1, 1)
    future_dates = pd.date_range(start=df['date'].max() + timedelta(days=1), periods=days_ahead)
    
    # Predict
    predictions = model.predict(future_days)
    
    forecast_df = pd.DataFrame({
        'date': future_dates,
        metric: predictions
    })
    
    return forecast_df

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Echolon+AI", use_container_width=True)
    st.title("🎯 Echolon AI")
    st.markdown("### Business Intelligence Platform")
    st.markdown("---")
    
    # Navigation
    st.markdown("## 📍 Navigation")
    
    pages = {
        "🏠 Dashboard": "Dashboard",
        "📊 Analytics": "Analytics",
        "🔮 Predictions": "Predictions",
        "💡 Recommendations": "Recommendations",
        "📝 What-If Analysis": "What-If Analysis",
        "🎨 Inventory": "Inventory",
        "📂 Upload Data": "Upload Data"
    }
    
    for page_name, page_id in pages.items():
        if st.sidebar.button(page_name, key=page_id, use_container_width=True):
            st.session_state.current_page = page_id
    
    st.markdown("---")
    
    # Demo data toggle
    st.markdown("## 📊 Using Demo Data")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.uploaded_data = None
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Load data
if st.session_state.uploaded_data is None:
    data = generate_demo_data()
else:
    data = st.session_state.uploaded_data

kpis = calculate_kpis(data)

# Main Content Area
if st.session_state.current_page == "Dashboard":
    st.title("📈 Real-time Business Intelligence & Analytics")
    
    # KPI Cards
# Render KPI strip using reusable function
    render_kpi_strip(kpis)
        
    # Date range filter
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=data['date'].min(),
            min_value=data['date'].min(),
            max_value=data['date'].max()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=data['date'].max(),
            min_value=data['date'].min(),
            max_value=data['date'].max()
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset Dates", use_container_width=True):
            st.rerun()
    
    # Filter data by date range
    filtered_data = data[
        (data['date'] >= pd.to_datetime(start_date)) & 
        (data['date'] <= pd.to_datetime(end_date))
    ]
    
    # Recalculate KPIs with filtered data
    kpis = calculate_kpis(filtered_data)
    
    st.markdown("---")

    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue Trend")
        st.markdown("**Daily Revenue**")
        fig = px.line(filtered_data, x='date', y='revenue', title='Daily Revenue')
        fig.update_layout(xaxis_title='Date', yaxis_title='Revenue ($)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered_data['date'], y=filtered_data['orders'], name='Orders', mode='lines'))
        fig.add_trace(go.Scatter(x=filtered_data['date'], y=filtered_data['customers'], name='Customers', mode='lines'))
        fig.update_layout(xaxis_title='Date', yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)    # Data Preview
    with st.expander("📊 View Data Preview"):
        st.dataframe(filtered_data.tail(20), use_container_width=True)
elif st.session_state.current_page == "Analytics":
    st.title("📊 Advanced Analytics")
    
    # Metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_daily_revenue = data['revenue'].mean()
        st.metric("Avg Daily Revenue", f"${avg_daily_revenue:,.2f}")
    
    with col2:
        avg_profit_margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 0
        st.metric("Avg Profit Margin", f"{avg_profit_margin:.2f}%")
    
    with col3:
        total_marketing = data['marketing_spend'].sum() if 'marketing_spend' in data.columns else 0
        st.metric("Total Marketing Spend", f"${total_marketing:,.0f}")
    
    with col4:
        avg_roas = data['roas'].mean() if 'roas' in data.columns else 0
        st.metric("Avg ROAS", f"{avg_roas:.2f}x")
    
    st.markdown("---")
    
    # Distribution Analysis
    st.subheader("📉 Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Revenue Distribution**")
        fig = px.histogram(data, x='revenue', nbins=30, title='Revenue Distribution')
        fig.update_layout(xaxis_title='Revenue ($)', yaxis_title='Frequency')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Orders Distribution**")
        fig = px.histogram(data, x='orders', nbins=30, title='Orders Distribution')
        fig.update_layout(xaxis_title='Orders', yaxis_title='Frequency')
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation Analysis
    st.subheader("🔗 Correlation Analysis")
    
    numeric_cols = ['revenue', 'orders', 'customers', 'profit', 'marketing_spend']
    available_cols = [col for col in numeric_cols if col in data.columns]
    
    if len(available_cols) >= 2:
        corr_matrix = data[available_cols].corr()
        
        fig = px.imshow(corr_matrix, 
                       text_auto=True, 
                       aspect="auto",
                       color_continuous_scale='RdBu_r',
                       title='Correlation Heatmap')
        st.plotly_chart(fig, use_container_width=True)
    
    # Time Series Decomposition
    st.subheader("📈 Trend Analysis")
    
    # Calculate moving averages
    data['revenue_ma7'] = data['revenue'].rolling(window=7).mean()
    data['revenue_ma30'] = data['revenue'].rolling(window=30).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['revenue'], name='Actual', mode='lines', opacity=0.3))
    fig.add_trace(go.Scatter(x=data['date'], y=data['revenue_ma7'], name='7-Day MA', mode='lines'))
    fig.add_trace(go.Scatter(x=data['date'], y=data['revenue_ma30'], name='30-Day MA', mode='lines'))
    fig.update_layout(title='Revenue with Moving Averages', xaxis_title='Date', yaxis_title='Revenue ($)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical Summary
    st.subheader("📊 Statistical Summary")
    st.dataframe(data[available_cols].describe(), use_container_width=True)

elif st.session_state.current_page == "Predictions":
    st.title("🔮 AI-Powered Predictions")
    
    st.markdown("### 📈 Revenue Forecasting")
    
    # Forecast settings
    col1, col2 = st.columns([3, 1])
    
    with col2:
        forecast_days = st.slider("Forecast Days Ahead", min_value=7, max_value=90, value=30)
    
    # Generate forecast
    forecast_df = forecast_metric(data, 'revenue', days_ahead=forecast_days)
    
    if forecast_df is not None:
        # Plot historical + forecast
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=data['date'], 
            y=data['revenue'],
            name='Historical',
            mode='lines',
            line=dict(color='blue')
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['revenue'],
            name='Forecast',
            mode='lines',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title=f'Revenue Forecast - Next {forecast_days} Days',
            xaxis_title='Date',
            yaxis_title='Revenue ($)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast metrics
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
    
    st.markdown("---")
    
    # Orders forecast
    st.markdown("### 📎 Orders Forecasting")
    
    forecast_orders = forecast_metric(data, 'orders', days_ahead=forecast_days)
    
    if forecast_orders is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['date'], y=data['orders'], name='Historical', mode='lines'))
        fig.add_trace(go.Scatter(x=forecast_orders['date'], y=forecast_orders['orders'], name='Forecast', mode='lines', line=dict(dash='dash')))
        fig.update_layout(title=f'Orders Forecast - Next {forecast_days} Days', xaxis_title='Date', yaxis_title='Orders')
        st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.markdown("### 💡 Predictive Insights")
    st.info("""
    **Key Findings:**
    - Revenue trend shows steady growth potential
    - Seasonal patterns detected in historical data
    - Forecasts based on linear regression model
    - Confidence intervals suggest moderate variability
    """)

elif st.session_state.current_page == "Recommendations":
    st.title("💡 AI Business Recommendations")
    
    # Calculate key metrics for recommendations
    avg_revenue = data['revenue'].mean()
    revenue_std = data['revenue'].std()
    revenue_trend = (data['revenue'].tail(30).mean() - data['revenue'].head(30).mean()) / data['revenue'].head(30).mean() * 100
    
    avg_profit_margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 0
    avg_roas = data['roas'].mean() if 'roas' in data.columns else 0
    
    # Generate recommendations
    st.markdown("### 🎯 Priority Recommendations")
    
    recommendations = []
    
    # Revenue recommendations
    if revenue_trend < 0:
        recommendations.append({
            'priority': 'High',
            'category': 'Revenue',
            'title': 'Address Declining Revenue Trend',
            'description': f'Revenue has declined by {abs(revenue_trend):.1f}% over the period. Consider promotional campaigns or new customer acquisition strategies.',
            'impact': 'High',
            'effort': 'Medium'
        })
    elif revenue_trend > 10:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Growth',
            'title': 'Capitalize on Positive Growth',
            'description': f'Revenue is growing at {revenue_trend:.1f}%. Scale successful channels and invest in customer retention.',
            'impact': 'High',
            'effort': 'Low'
        })
    
    # Profit margin recommendations
    if avg_profit_margin < 20:
        recommendations.append({
            'priority': 'High',
            'category': 'Profitability',
            'title': 'Improve Profit Margins',
            'description': f'Current profit margin is {avg_profit_margin:.1f}%. Review cost structure and pricing strategy.',
            'impact': 'High',
            'effort': 'High'
        })
    
    # Marketing recommendations
    if avg_roas < 2:
        recommendations.append({
            'priority': 'High',
            'category': 'Marketing',
            'title': 'Optimize Marketing Spend',
            'description': f'ROAS is {avg_roas:.2f}x. Re-evaluate marketing channels and focus on higher-performing campaigns.',
            'impact': 'Medium',
            'effort': 'Medium'
        })
    
    # Variability recommendations
    cv = (revenue_std / avg_revenue) * 100
    if cv > 30:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Stability',
            'title': 'Reduce Revenue Volatility',
            'description': f'Revenue variability is high ({cv:.1f}% CV). Consider diversifying revenue streams or implementing subscription models.',
            'impact': 'Medium',
            'effort': 'High'
        })
    
    # Display recommendations
    for idx, rec in enumerate(recommendations, 1):
        with st.expander(f"{idx}. [{rec['priority']} Priority] {rec['title']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Category:** {rec['category']}")
            with col2:
                st.markdown(f"**Impact:** {rec['impact']}")
            with col3:
                st.markdown(f"**Effort:** {rec['effort']}")
            
            st.markdown(f"**Description:** {rec['description']}")
    
    if not recommendations:
        st.success("✅ Your business metrics are performing well! Keep up the good work.")
    
    st.markdown("---")
    
    # Performance Score
    st.markdown("### 🏆 Business Health Score")
    
    scores = []
    if revenue_trend > 0:
        scores.append(25)
    if avg_profit_margin > 20:
        scores.append(25)
    if avg_roas > 3:
        scores.append(25)
    if cv < 20:
        scores.append(25)
    
    health_score = sum(scores)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if health_score >= 75:
            st.success(f"🌟 Excellent: {health_score}/100")
        elif health_score >= 50:
            st.info(f"📈 Good: {health_score}/100")
        else:
            st.warning(f"⚠️ Needs Attention: {health_score}/100")
    
    with col2:
        st.progress(health_score/100)

elif st.session_state.current_page == "What-If Analysis":
    st.title("📝 What-If Scenario Analysis")
    
    st.markdown("### 📊 Scenario Modeling")
    st.info("Adjust the sliders below to see how changes in key metrics affect your business outcomes.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Revenue Assumptions")
        revenue_change = st.slider("Revenue Change (%)", min_value=-50, max_value=100, value=0, step=5)
        
        st.markdown("#### 💰 Cost Assumptions")
        cost_change = st.slider("Cost Change (%)", min_value=-50, max_value=100, value=0, step=5)
    
    with col2:
        st.markdown("#### 📊 Marketing Assumptions")
        marketing_change = st.slider("Marketing Spend Change (%)", min_value=-50, max_value=100, value=0, step=5)
        
        st.markdown("#### 👥 Customer Assumptions")
        customer_change = st.slider("Customer Growth (%)", min_value=-50, max_value=100, value=0, step=5)
    
    # Calculate scenarios
    base_revenue = data['revenue'].sum()
    base_cost = data['cost'].sum() if 'cost' in data.columns else base_revenue * 0.6
    base_profit = base_revenue - base_cost
    base_margin = (base_profit / base_revenue) * 100
    
    scenario_revenue = base_revenue * (1 + revenue_change/100)
    scenario_cost = base_cost * (1 + cost_change/100)
    scenario_profit = scenario_revenue - scenario_cost
    scenario_margin = (scenario_profit / scenario_revenue) * 100
    
    st.markdown("---")
    st.markdown("### 📄 Scenario Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${scenario_revenue:,.0f}",
            delta=f"${scenario_revenue - base_revenue:,.0f}"
        )
    
    with col2:
        st.metric(
            "Total Profit",
            f"${scenario_profit:,.0f}",
            delta=f"${scenario_profit - base_profit:,.0f}"
        )
    
    with col3:
        st.metric(
            "Profit Margin",
            f"{scenario_margin:.1f}%",
            delta=f"{scenario_margin - base_margin:.1f}%"
        )
    
    # Visualize comparison
    st.markdown("### 📉 Base vs Scenario Comparison")
    
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
    
    fig.update_layout(barmode='group', title='Financial Comparison')
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.current_page == "Inventory":
    st.title("📦 Inventory Management Analytics")
    
    if 'inventory_units' not in data.columns:
        st.warning("⚠️ Inventory data not available in current dataset.")
    else:
        # Inventory KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_inventory = data['inventory_units'].mean()
            st.metric("Avg Inventory Level", f"{avg_inventory:,.0f} units")
        
        with col2:
            max_inventory = data['inventory_units'].max()
            st.metric("Peak Inventory", f"{max_inventory:,.0f} units")
        
        with col3:
            min_inventory = data['inventory_units'].min()
            st.metric("Lowest Inventory", f"{min_inventory:,.0f} units")
        
        with col4:
            inventory_volatility = data['inventory_units'].std()
            st.metric("Inventory Volatility", f"{inventory_volatility:,.0f} units")
        
        st.markdown("---")
        
        # Inventory Trend
        st.subheader("📈 Inventory Levels Over Time")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['inventory_units'],
            mode='lines',
            name='Inventory Units',
            fill='tozeroy'
        ))
        
        # Add average line
        fig.add_hline(y=avg_inventory, line_dash="dash", line_color="red", annotation_text="Average")
        
        fig.update_layout(
            title='Daily Inventory Levels',
            xaxis_title='Date',
            yaxis_title='Units'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Inventory turnover analysis
        st.subheader("🔄 Inventory Turnover Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate turnover ratio
            total_sales = data['orders'].sum()
            turnover_ratio = total_sales / avg_inventory if avg_inventory > 0 else 0
            
            st.metric("Inventory Turnover Ratio", f"{turnover_ratio:.2f}x")
            st.info("""
            **Interpretation:**
            - Higher ratio indicates faster inventory movement
            - Typical good ratio: 5-10x per year
            - Too high: Risk of stockouts
            - Too low: Excess capital tied up
            """)
        
        with col2:
            # Days inventory outstanding
            days_inventory = 365 / turnover_ratio if turnover_ratio > 0 else 0
            st.metric("Days Inventory Outstanding", f"{days_inventory:.0f} days")
            
            st.info("""
            **Interpretation:**
            - Average days to sell inventory
            - Lower is generally better
            - Industry benchmarks vary widely
            - Monitor trends over time
            """)
        
        # Inventory vs Sales correlation
        st.subheader("🔗 Inventory vs Sales Correlation")
        
        fig = px.scatter(
            data,
            x='inventory_units',
            y='orders',
            trendline='ols',
            title='Inventory Units vs Daily Orders'
        )
        fig.update_layout(
            xaxis_title='Inventory Units',
            yaxis_title='Daily Orders'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.markdown("### 💡 Inventory Insights")
        
        inventory_insights = []
        
        if turnover_ratio < 5:
            inventory_insights.append("⚠️ Low turnover ratio detected. Consider reducing inventory levels or increasing sales efforts.")
        elif turnover_ratio > 15:
            inventory_insights.append("🚨 High turnover ratio. Monitor for potential stockouts and consider increasing safety stock.")
        
        if inventory_volatility > avg_inventory * 0.3:
            inventory_insights.append("📉 High inventory volatility. Implement better demand forecasting and planning.")
        
        if inventory_insights:
            for insight in inventory_insights:
                st.warning(insight)
        else:
            st.success("✅ Inventory levels appear well-managed!")

elif st.session_state.current_page == "Upload Data":
    st.title("📂 Upload Your Data")
    
    st.markdown("Upload your business data to get personalized insights.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['date', 'revenue', 'orders', 'customers']
            missing_columns = [col for col in required_columns if col not in df.columns.str.lower()]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                st.info("Your CSV must include: date, revenue, orders, customers")
            else:
                # Normalize column names to lowercase
                df.columns = df.columns.str.lower()
                
                # Validate data types and content
                validation_errors = []
                
                # Check date column
                try:
                    df['date'] = pd.to_datetime(df['date'])
                except:
                    validation_errors.append("📅 Date column must be in a valid date format (YYYY-MM-DD recommended)")
                
                # Check numeric columns
                for col in ['revenue', 'orders', 'customers']:
                    if col in df.columns:
                        try:
                            df[col] = pd.to_numeric(df[col], errors='raise')
                            if (df[col] < 0).any():
                                validation_errors.append(f"⚠️ {col.capitalize()} contains negative values")
                        except:
                            validation_errors.append(f"🔢 {col.capitalize()} column must contain only numbers")
                
                # Check for empty data
                if len(df) == 0:
                    validation_errors.append("📋 CSV file is empty")
                
                # Display validation results
                if validation_errors:
                    st.error("**Data Validation Failed:**")
                    for error in validation_errors:
                        st.markdown(f"- {error}")
                else:
                    # Data is valid - show preview and quality score
                    st.success(f"✅ Successfully loaded {len(df)} rows!")
                    
                    # Calculate data quality score
                    total_cells = len(df) * len(df.columns)
                    missing_cells = df.isnull().sum().sum()
                    quality_score = int((1 - missing_cells/total_cells) * 100)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Rows", len(df))
                    
                    with col2:
                        st.metric("Data Quality", f"{quality_score}%")
                    
                    with col3:
                        date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
                        st.metric("Date Range", date_range)
                    
                    st.dataframe(df.head(10))
                    
                    if st.button("✅ Use This Data"):
                        # Add derived metrics if not present
                        if 'profit' not in df.columns and 'cost' in df.columns:
                            df['profit'] = df['revenue'] - df['cost']
                            df['profit_margin'] = (df['profit'] / df['revenue'] * 100).round(2)
                        
                        if 'roas' not in df.columns and 'marketing_spend' in df.columns:
                            df['roas'] = (df['revenue'] / df['marketing_spend']).round(2)
                        
                        st.session_state.uploaded_data = df
                        st.session_state.data_source = 'uploaded'
                        st.success("Data uploaded successfully! Navigate to Dashboard to see your insights.")
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.info("Please ensure your CSV is properly formatted")
    
    st.markdown("**Expected CSV format:**")
    st.markdown("- date: Date column (YYYY-MM-DD)")
    st.markdown("- revenue: Revenue amount")
    st.markdown("- orders: Number of orders")
    st.markdown("- customers: Number of customers")
    st.markdown("- cost: Cost amount (optional)")
    st.markdown("- marketing_spend: Marketing spend (optional)")
    st.markdown("- inventory_units: Inventory units (optional)")
    
    # Clear Data & Reset Button
    st.markdown("---")
    st.markdown("### 🔄 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.get('data_source') == 'uploaded':
            st.info("✅ Currently using uploaded data")
        else:
            st.info("📊 Currently using demo data")
    
    with col2:
        if st.button("🔄 Clear Data & Reset to Demo", type="secondary"):
            # Clear uploaded data
            if 'uploaded_data' in st.session_state:
                del st.session_state.uploaded_data
            st.session_state.data_source = 'demo'
            st.success("✅ Reset to demo data! Refresh the page to see changes.")
            st.rerun()
