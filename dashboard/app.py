import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

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
    st.session_state.data_source = 'demo'
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Sample data generator for demo
def generate_demo_data():
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    data = pd.DataFrame({
        'date': dates,
        'revenue': np.random.normal(50000, 10000, len(dates)).cumsum() / 100,
        'orders': np.random.poisson(100, len(dates)),
        'customers': np.random.poisson(50, len(dates)),
        'cost': np.random.normal(30000, 5000, len(dates)).cumsum() / 100,
        'marketing_spend': np.random.normal(5000, 1000, len(dates)),
        'inventory_units': np.random.randint(500, 2000, len(dates))
    })
    data['profit'] = data['revenue'] - data['cost']
    data['profit_margin'] = (data['profit'] / data['revenue'] * 100).round(2)
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
        'revenue_growth': revenue_growth,
        'total_orders': int(total_orders),
        'orders_growth': orders_growth,
        'total_customers': int(total_customers),
        'customers_growth': customers_growth,
        'avg_order_value': avg_order_value,
        'total_profit': total_profit,
        'avg_profit_margin': avg_profit_margin
    }

# Sidebar Navigation
with st.sidebar:
    st.title("📊 Echolon AI")
    st.markdown("### Business Intelligence Platform")
    st.markdown("---")
    
    # Navigation
    st.markdown("#### 📢 Navigation")
    pages = [
        "🏠 Dashboard",
        "📊 Analytics",
        "🔮 Predictions",
        "💡 Recommendations",
        "📈 What-If Analysis",
        "📦 Inventory",
        "📎 Upload Data"
    ]
    
    for page in pages:
        if st.button(page, key=page, use_container_width=True):
            st.session_state.current_page = page.split(' ', 1)[1]
    
    st.markdown("---")
    
    # Data source indicator
    if st.session_state.data_source == 'demo':
        st.info("📢 Using Demo Data")
    else:
        st.success("✅ Using Your Data")
    
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Get data
if st.session_state.uploaded_data is not None:
    df = st.session_state.uploaded_data
else:
    df = generate_demo_data()

kpis = calculate_kpis(df)

# Main Content based on current page
if st.session_state.current_page == 'Dashboard':
    st.title("🚀 Echolon AI Dashboard")
    st.markdown("### Real-time Business Intelligence & Analytics")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${kpis.get('total_revenue', 0):,.0f}",
            f"{kpis.get('revenue_growth', 0):.1f}%"
        )
    
    with col2:
        st.metric(
            "Total Orders",
            f"{kpis.get('total_orders', 0):,}",
            f"{kpis.get('orders_growth', 0):.1f}%"
        )
    
    with col3:
        st.metric(
            "Total Customers",
            f"{kpis.get('total_customers', 0):,}",
            f"{kpis.get('customers_growth', 0):.1f}%"
        )
    
    with col4:
        st.metric(
            "Avg Order Value",
            f"${kpis.get('avg_order_value', 0):.2f}",
            f"{kpis.get('avg_profit_margin', 0):.1f}% margin"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        if 'date' in df.columns:
            fig = px.line(df, x='date', y='revenue', title='Daily Revenue')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Upload data with 'date' and 'revenue' columns to see trends")
    
    with col2:
        st.subheader("📊 Orders & Customers")
        if 'date' in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['orders'], name='Orders', mode='lines'))
            fig.add_trace(go.Scatter(x=df['date'], y=df['customers'], name='Customers', mode='lines'))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Upload data with 'date', 'orders', and 'customers' columns")
    
    # Data preview
    with st.expander("📊 View Data Preview"):
        st.dataframe(df.head(50), use_container_width=True)

elif st.session_state.current_page == 'Upload Data':
    st.title("📎 Upload Your Business Data")
    st.markdown("### Upload CSV file to analyze your business metrics")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your business data in CSV format"
    )
    
    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            st.success(f"✅ Successfully loaded {len(df_uploaded)} rows!")
            
            st.subheader("Data Preview")
            st.dataframe(df_uploaded.head(10), use_container_width=True)
            
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column': df_uploaded.columns,
                'Type': df_uploaded.dtypes.values,
                'Non-Null Count': df_uploaded.count().values,
                'Null Count': df_uploaded.isnull().sum().values
            })
            st.dataframe(col_info, use_container_width=True)
            
            if st.button("✅ Use This Data", type="primary"):
                st.session_state.uploaded_data = df_uploaded
                st.session_state.data_source = 'uploaded'
                st.success("Data loaded successfully! Navigate to Dashboard to see your insights.")
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    
    st.markdown("---")
    st.info("💡 Expected columns: date, revenue, orders, customers, cost, profit, etc.")

elif st.session_state.current_page == 'Analytics':
    st.title("📊 Advanced Analytics")
    st.markdown("### Deep dive into your business metrics")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    with col1:
        period = st.selectbox("Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
    
    st.markdown("---")
    
    # Profit Analysis
    if 'profit' in df.columns:
        st.subheader("💰 Profit Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Profit", f"${kpis.get('total_profit', 0):,.0f}")
            st.metric("Avg Profit Margin", f"{kpis.get('avg_profit_margin', 0):.2f}%")
        
        with col2:
            if 'date' in df.columns:
                fig = px.area(df, x='date', y='profit', title='Profit Over Time')
                st.plotly_chart(fig, use_container_width=True)
    
    # Coming soon sections
    st.info("🚀 More analytics features coming soon: Cohort analysis, Customer lifetime value, Churn prediction, and more!")

else:
    st.title(f"🚧 {st.session_state.current_page}")
    st.info(f"The {st.session_state.current_page} page is under development. Core functionality will be added progressively.")
    st.markdown("### Features Coming Soon:")
    if st.session_state.current_page == 'Predictions':
        st.markdown("- Revenue forecasting\n- Demand prediction\n- Customer churn prediction\n- Inventory optimization")
    elif st.session_state.current_page == 'Recommendations':
        st.markdown("- AI-powered business insights\n- Action recommendations\n- Opportunity identification\n- Risk alerts")
    elif st.session_state.current_page == 'What-If Analysis':
        st.markdown("- Scenario modeling\n- Impact simulation\n- Strategy comparison\n- ROI calculator")
    elif st.session_state.current_page == 'Inventory':
        st.markdown("- Stock level monitoring\n- Reorder point calculation\n- Turnover analysis\n- Supplier performance")

st.markdown("---")
st.caption("© 2025 Echolon AI - Intelligent Business Analytics Platform")
