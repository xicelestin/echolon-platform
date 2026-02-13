"""Goals & Target Tracking - Set and track business goals."""
import streamlit as st
import pandas as pd
from utils import get_goal_progress, calculate_key_metrics


def render_goals_page(data=None, kpis=None, format_currency=None, format_percentage=None):
    """Render the Goals & Target Tracking page."""
    if data is None:
        data = st.session_state.get('demo_data')
    if format_currency is None:
        format_currency = lambda v, d=0: f"${v:,.0f}" if v < 1e6 else f"${v/1e6:.1f}M"
    if format_percentage is None:
        format_percentage = lambda v, d=1: f"{v:.1f}%"

    st.title("🎯 Goals & Target Tracking")
    st.markdown("### Set quarterly targets and track your progress")

    # Initialize goals in session state
    if 'goals' not in st.session_state:
        metrics = calculate_key_metrics(data) if data is not None and not data.empty else {}
        total_rev = data['revenue'].sum() if data is not None and 'revenue' in data.columns else 500000
        st.session_state.goals = {
            'revenue': {'target': total_rev * 1.2, 'current': total_rev},
            'profit_margin': {'target': 45, 'current': 40},
            'customers': {'target': 3000, 'current': 2000},
            'roas': {'target': 5.0, 'current': 3.5}
        }

    goals = st.session_state.goals

    # Current metrics from data
    if data is not None and not data.empty:
        goals['revenue']['current'] = data['revenue'].sum()
        if 'profit_margin' in data.columns:
            goals['profit_margin']['current'] = data['profit_margin'].mean()
        if 'customers' in data.columns:
            goals['customers']['current'] = int(data['customers'].iloc[-1])
        if 'roas' in data.columns:
            goals['roas']['current'] = data['roas'].mean()

    st.markdown("---")
    st.subheader("📊 Your Goals")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("💰 Revenue Goal", expanded=True):
            rev_target = st.number_input("Target Revenue ($)", value=int(goals['revenue']['target']), step=10000, key="goal_rev")
            progress = get_goal_progress(goals['revenue']['current'], rev_target)
            st.progress(min(progress['progress'] / 100, 1.0))
            st.markdown(f"**Current:** {format_currency(goals['revenue']['current'])} | **Target:** {format_currency(rev_target)}")
            st.caption(progress['message'])

        with st.expander("👥 Customer Goal", expanded=True):
            cust_target = st.number_input("Target Customers", value=int(goals['customers']['target']), step=100, key="goal_cust")
            progress = get_goal_progress(goals['customers']['current'], cust_target)
            st.progress(min(progress['progress'] / 100, 1.0))
            st.markdown(f"**Current:** {goals['customers']['current']:,.0f} | **Target:** {cust_target:,.0f}")
            st.caption(progress['message'])

    with col2:
        with st.expander("📈 Profit Margin Goal", expanded=True):
            margin_target = st.number_input("Target Margin (%)", value=int(goals['profit_margin']['target']), step=1, key="goal_margin")
            progress = get_goal_progress(goals['profit_margin']['current'], margin_target)
            st.progress(min(progress['progress'] / 100, 1.0))
            st.markdown(f"**Current:** {format_percentage(goals['profit_margin']['current'])} | **Target:** {format_percentage(margin_target)}")
            st.caption(progress['message'])

        with st.expander("⚡ ROAS Goal", expanded=True):
            roas_target = st.number_input("Target ROAS (x)", value=float(goals['roas']['target']), step=0.5, format="%.1f", key="goal_roas")
            progress = get_goal_progress(goals['roas']['current'], roas_target)
            st.progress(min(progress['progress'] / 100, 1.0))
            st.markdown(f"**Current:** {goals['roas']['current']:.1f}x | **Target:** {roas_target:.1f}x")
            st.caption(progress['message'])

    st.markdown("---")
    st.subheader("📋 Summary")
    achieved = sum([
        1 if goals['revenue']['current'] >= rev_target else 0,
        1 if goals['profit_margin']['current'] >= margin_target else 0,
        1 if goals['customers']['current'] >= cust_target else 0,
        1 if goals['roas']['current'] >= roas_target else 0
    ])
    st.info(f"You're on track with **{achieved}/4** goals. Keep pushing!")
