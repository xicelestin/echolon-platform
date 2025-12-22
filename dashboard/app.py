import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Import page render functions
try:
    from pages_predictions import render_predictions_page
    from pages_recommendations import render_recommendations_page
    from pages_whatif import render_whatif_page
    from pages_inventory_ops import render_inventory_page
except ImportError as e:
    # Fallback if page modules can't be imported
    render_predictions_page = None
    render_recommendations_page = None
    render_whatif_page = None
    render_inventory_page = None

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
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value,
        'total_profit': total_profit,
        'avg_profit_margin': avg_profit_margin,
        'revenue_growth': revenue_growth,
        'orders_growth': orders_growth,
        'customers_growth': customers_growth
    }

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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${kpis['total_revenue']:,.0f}",
            delta=f"{kpis['revenue_growth']:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Total Orders",
            value=f"{kpis['total_orders']:,.0f}",
            delta=f"{kpis['orders_growth']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Total Customers",
            value=f"{kpis['total_customers']:,.0f}",
            delta=f"{kpis['customers_growth']:.1f}%"
        )
    
    with col4:
        st.metric(
            label="Avg Order Value",
            value=f"${kpis['avg_order_value']:.2f}",
            delta=f"{kpis['avg_profit_margin']:.1f}% margin"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue Trend")
        st.markdown("**Daily Revenue**")
        
        fig = px.line(data, x='date', y='revenue', title='Daily Revenue')
        fig.update_layout(xaxis_title='Date', yaxis_title='Revenue ($)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Orders & Customers")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['date'], y=data['orders'], name='Orders', mode='lines'))
        fig.add_trace(go.Scatter(x=data['date'], y=data['customers'], name='Customers', mode='lines'))
        fig.update_layout(xaxis_title='Date', yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)
    
    # Data Preview
    with st.expander("📊 View Data Preview"):
        st.dataframe(data.tail(20), use_container_width=True)
    

elif st.session_state.current_page == "Analytics":
    st.title("📊 Advanced Analytics")
    st.info("Advanced analytics features coming soon...")
    
    # Placeholder for analytics
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue Distribution")
        fig = px.histogram(data, x='revenue', nbins=50)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Orders Distribution")
        fig = px.histogram(data, x='orders', nbins=50)
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.current_page == "Predictions":
        if render_predictions_page:
                    render_predictions_page()
    else:
                st.title("🔮 AI-Powered Predictions")
                st.info("Predictive analytics features coming soon...")

    elif st.session_state.current_page == "Recommendations":
        if render_recommendations_page:
                    render_recommendations_page()
            else:
                    st.title("💡 AI Recommendations")
                                        st.info("AI recommendation engine coming soon...")

elif st.session_state.current_page == "What-If Analysis":
        if render_whatif_page:
        render_whatif_page()
        else:
        st.title("📈 What-If Analysis")
            st.info("What-If analysis tools coming soon...")
            
    elif st.session_state.current_page == "Inventory":
                            if render_inventory_page:
                                render_inventory_page()
            else:
                    st.title("📦 Inventory Management")
            st.info("Inventory management features coming soon...")

elif st.session_state.current_page == "Upload Data":
    st.title("📂 Upload Your Data")
    st.markdown("Upload your business data to get personalized insights.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Successfully loaded {len(df)} rows!")
            st.dataframe(df.head())
            
            if st.button("Use This Data"):
                st.session_state.uploaded_data = df
                st.session_state.data_source = 'uploaded'
                st.success("Data uploaded successfully! Navigate to Dashboard to see your insights.")
                st.rerun()
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    st.markdown("---")
    st.markdown("**Expected CSV format:**")
    st.markdown("- date: Date column (YYYY-MM-DD)")
    st.markdown("- revenue: Revenue amount")
    st.markdown("- orders: Number of orders")
    st.markdown("- customers: Number of customers")
    st.markdown("- cost: Cost amount (optional)")
    st.markdown("- marketing_spend: Marketing spend (optional)")
    st.markdown("- inventory_units: Inventory units (optional)")
