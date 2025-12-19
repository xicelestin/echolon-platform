# DEPLOY 2025-12-19 05:45 UTC - FORCE STREAMLIT CACHE CLEAR
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import requests
import os
import time
print('DEBUG: Starting custom module imports...')
from business_owner_fixes import (show_personalized_onboarding, render_kpi_with_context, personalize_insights, show_tactical_recommendation, render_what_if_presets, get_health_badge, render_kpi_with_benchmark, generate_actionable_insights, display_actionable_insight, get_priority_score)
print('DEBUG: business_owner_fixes imported successfully')
from data_validation import DataValidator, validate_csv_file
print('DEBUG: data_validation imported successfully')
from performance_optimizer import PerformanceOptimizer, cached_data_processing
print('DEBUG: performance_optimizer imported successfully')
from data_transformer import DataTransformer, get_transformation_options
print('DEBUG: data_transformer imported successfully')
print('DEBUG: All imports completed successfully!')
st.set_page_config(page_title="Echolon AI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Force redeploy - 2025-12-17 FINAL FIX - CUSTOM CSS
st.markdown("""
<style>
.sidebar-header h2 {margin: 0; font-size: 24px; font-weight: 700; color: #fff;}
.sidebar-section {font-size: 11px; font-weight: 700; text-transform: uppercase; color: #888; padding: 16px 0 8px 0;}
.kpi-card {background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 24px; border-radius: 12px; border-left: 4px solid #ff9500; transition: all 0.3s;}
.kpi-card:hover {transform: translateY(-4px); box-shadow: 0 12px 32px rgba(255,149,0,0.25);}
.kpi-card .icon {font-size: 32px; margin-bottom: 12px;}
.kpi-card .title {font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600;}
.kpi-card .metric {font-size: 32px; font-weight: 700; color: #fff; margin: 4px 0;}
.kpi-card .delta {font-size: 12px; color: #90ee90; font-weight: 500; margin-top: 8px;}
.data-badge {display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-bottom: 16px;}
.data-badge.demo {background: #1e3c72; color: #a0a0a0; border: 1px solid #2a5298;}
.data-badge.uploaded {background: #1e5c3c; color: #90ee90; border: 1px solid #2a7c56;}
.feature-card {background: rgba(255,149,0,0.08); border: 1px solid #ff9500; border-radius: 8px; padding: 20px; transition: all 0.3s;}
.feature-card:hover {background: rgba(255,149,0,0.15); border-color: #ffb84d; box-shadow: 0 4px 16px rgba(255,149,0,0.15);}
.page-header h1 {font-size: 36px; font-weight: 700; margin: 0; letter-spacing: -0.5px;}
.page-header p {font-size: 14px; color: #a0a0a0; margin: 8px 0 0 0;}
.last-updated {font-size: 12px; color: #888; text-align: right; padding: 12px 0;}
hr {border: none; border-top: 1px solid #1a1f38; margin: 24px 0;}
</style>
""", unsafe_allow_html=True)

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# ===================  BENCHMARKS CONSTANT  ===================
BENCHMARKS = {
    "revenue": {
        "industry_avg": 1500000,
        "top_25_percent": 3000000,
        "small_business_avg": 500000,
        "saas_avg": 2000000,
        "ecommerce_avg": 1200000
    },
    "churn_rate": {
        "industry_avg": 5.0,
        "top_25_percent": 2.0,
        "saas_avg": 5.0,
        "ecommerce_avg": 15.0,
        "b2b_avg": 3.0
    },
    "cac_payback_period": {
        "industry_avg": 12,
        "top_25_percent": 6,
        "saas_avg": 12,
        "ecommerce_avg": 3,
        "b2b_avg": 18
    },
    "ltv_cac_ratio": {
        "industry_avg": 3.0,
        "top_25_percent": 5.0,
        "saas_avg": 3.0,
        "ecommerce_avg": 2.5,
        "b2b_avg": 4.0
    },
    "conversion_rate": {
        "industry_avg": 2.5,
        "top_25_percent": 5.0,
        "ecommerce_avg": 2.0,
        "saas_avg": 3.0,
        "b2b_avg": 1.5
    },
    "customer_acquisition_cost": {
        "industry_avg": 250,
        "top_25_percent": 100,
        "saas_avg": 300,
        "ecommerce_avg": 50,
        "b2b_avg": 500
    }
}

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'demo'
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = datetime.now()
if 'baseline' not in st.session_state:
    st.session_state.baseline = {"revenue": 100000, "marketing": 20000, "churn": 0.05, "growth": 0.08, "inventory": 1000}


def calculate_kpis_from_data():
    """Calculate KPIs from uploaded data - requires user to upload CSV."""
    if st.session_state.uploaded_data is None or st.session_state.uploaded_data.empty:
        return {}
    
    df = st.session_state.uploaded_data
