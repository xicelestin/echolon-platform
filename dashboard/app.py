import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

from components import create_line_chart, create_bar_chart, COLORS, COLOR_PALETTE
from utils import create_multi_format_export, create_download_button
from utils import calculate_business_health_score, calculate_period_comparison
from utils.metrics_utils import forecast_revenue
from components import display_business_health_score, display_metric_with_comparison, display_key_metrics_grid

# Page Imports
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
from pages_analytics import render_analytics_page
from pages_predictions import render_predictions_page
from pages_recommendations import render_recommendations_page
from pages_whatif import render_whatif_page  # Temporarily commented - has IndentationErrorfrom pages_inventory_optimization import render_inventory_optimization_page

from auth import require_authentication, render_user_info
if not require_authentication():
    st.stop()

st.set_page_config(page_title="Echolon AI", page_icon="📊", layout="wide")

def format_currency(value, decimals=0):
    if value >= 1e6: return f"${value/1e6:.{decimals}f}M"
    if value >= 1e3: return f"${value/1e3:.{decimals}f}K"
    return f"${value:,.{decimals}f}"

def format_percentage(value, decimals=1): return f"{value:.{decimals}f}%"
def format_multiplier(value, decimals=2): return f"{value:.{decimals}f}x"
def format_number(value, decimals=0): return f"{value:,.{decimals}f}"

if 'current_page' not in st.session_state: st.session_state.current_page = 'Dashboard'

@st.cache_data
def load_data():
    dates = pd.date_range(start='2024-01-01', periods=365, freq='D')
    df = pd.DataFrame({
        'date': dates,
        'revenue': np.random.normal(5000, 500, 365).cumsum(),
        'orders': np.random.poisson(100, 365),
        'customers': np.random.poisson(50, 365),
        'marketing_spend': np.random.normal(1000, 100, 365),
        'inventory_units': np.random.randint(100, 1000, 365),
        'roas': np.random.uniform(2, 5, 365)
    })
    df['profit'] = df['revenue'] * 0.4
    df['profit_margin'] = 40.0
    df['avg_order_value'] = df['revenue'] / df['orders']
    return df

data = load_data()
kpis = {'total_revenue': data['revenue'].sum(), 'roas': data['roas'].mean()}

with st.sidebar:
    st.title("Echolon AI")
    for p in ["Dashboard", "Analytics", "Predictions", "Recommendations", "What-If Analysis", "Inventory", "Customer Insights", "Inventory & Demand", "Anomalies & Alerts", "Inventory Optimization", "Margin Analysis", "Smart Alerts", "Cohort Analysis", "Customer LTV", "Revenue Attribution", "Competitive Benchmark", "Data Sources"]:
        if st.button(p, use_container_width=True):
            st.session_state.current_page = p
            st.rerun()

p = st.session_state.current_page
args = (data, kpis, format_currency, format_percentage, format_multiplier)

if p == "Dashboard": st.title("Dashboard")
            pass  # Dashboard content will be added here
elif p == "Analytics": render_analytics_page(*args)
elif p == "Predictions": render_predictions_page()
elif p == "Recommendations": render_recommendations_page()
elif p == "What-If Analysis": render_whatif_page()
        
    elif p == "Inventory": render_inventory_page(*args)elif p == "Inventory Optimization": render_inventory_optimization_page(data, kpis, format_currency, format_percentage, format_number)
elif p == "Customer Insights": render_customer_insights_page(*args)
elif p == "Inventory & Demand": render_inventory_demand_page(*args)
elif p == "Anomalies & Alerts": render_anomalies_alerts_page(*args)
elif p == "Margin Analysis": render_margin_analysis_page(*args)
elif p == "Smart Alerts": render_smart_alerts_page(*args)
elif p == "Cohort Analysis": render_cohort_analysis_page(*args)
elif p == "Customer LTV": render_customer_ltv_page(*args)
elif p == "Revenue Attribution": render_revenue_attribution_page(*args)
elif p == "Competitive Benchmark": render_competitive_benchmark_page(*args)
elif p == "Data Sources": render_data_sources_page()
