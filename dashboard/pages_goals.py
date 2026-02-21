"""Goals & Target Tracking - Set and track business goals."""
import streamlit as st
import pandas as pd
from utils import get_goal_progress, calculate_key_metrics


def render_goals_page(data=None, kpis=None, format_currency=None, format_percentage=None, format_count=None):
    """Render the Goals & Target Tracking page."""
    if data is None:
        data = st.session_state.get('current_data')
        if data is None:
            data = st.session_state.get('uploaded_data')
    if format_currency is None:
        format_currency = lambda v, d=0: f"${v:,.0f}" if v < 1e6 else f"${v/1e6:.1f}M"
    if format_percentage is None:
        format_percentage = lambda v, d=1: f"{v:.1f}%"
    if format_count is None:
        format_count = lambda v: f"{int(round(v)):,}"
    kpis = kpis or {}
    winfo = kpis.get('window_info', {})
    window_label = winfo.get('label', 'Last 90 Days')

    st.title("🎯 Goals & Target Tracking")
    st.markdown("### Set quarterly targets and track your progress")
    st.caption(f"**Goal window:** {window_label} — all goals evaluated against this period.")

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

    # Current metrics from data (same canonical source as Dashboard)
    roas_unavailable = kpis.get('roas_unavailable', True)
    if data is not None and not data.empty:
        goals['revenue']['current'] = data['revenue'].sum()
        if 'profit_margin' in data.columns:
            goals['profit_margin']['current'] = data['profit_margin'].mean()
        if 'customers' in data.columns and len(data) > 0:
            goals['customers']['current'] = int(data['customers'].iloc[-1])  # Latest count, not sum
        if not roas_unavailable and kpis.get('roas') is not None:
            goals['roas']['current'] = kpis['roas']
        elif 'roas' in data.columns and not roas_unavailable:
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
        st.markdown("<div style='margin:0.75rem 0;'></div>", unsafe_allow_html=True)
        with st.expander("👥 Customer Goal", expanded=True):
            cust_target = st.number_input("Target Customers", value=int(goals['customers']['target']), step=100, key="goal_cust")
            progress = get_goal_progress(goals['customers']['current'], cust_target)
            st.progress(min(progress['progress'] / 100, 1.0))
            st.markdown(f"**Current:** {format_count(goals['customers']['current'])} | **Target:** {format_count(cust_target)}")
            st.caption(progress['message'])
        st.markdown("<div style='margin:0.75rem 0;'></div>", unsafe_allow_html=True)

    with col2:
        with st.expander("📈 Profit Margin Goal", expanded=True):
            margin_target = st.number_input("Target Margin (%)", value=int(goals['profit_margin']['target']), step=1, key="goal_margin")
            progress = get_goal_progress(goals['profit_margin']['current'], margin_target)
            st.progress(min(progress['progress'] / 100, 1.0))
            st.markdown(f"**Current:** {format_percentage(goals['profit_margin']['current'])} | **Target:** {format_percentage(margin_target)}")
            st.caption(progress['message'])
        st.markdown("<div style='margin:0.75rem 0;'></div>", unsafe_allow_html=True)
        with st.expander("⚡ ROAS Goal", expanded=True):
            roas_target = st.number_input("Target ROAS (x)", value=float(goals['roas']['target']), step=0.5, format="%.1f", key="goal_roas")
            if roas_unavailable:
                st.warning("**N/A** — Connect `ad_spend` or `marketing_spend` in Data Sources to track ROAS.")
                st.caption("Map marketing spend to enable this goal.")
            else:
                progress = get_goal_progress(goals['roas']['current'], roas_target)
                st.progress(min(progress['progress'] / 100, 1.0))
                st.markdown(f"**Current:** {goals['roas']['current']:.1f}x | **Target:** {roas_target:.1f}x")
                st.caption(progress['message'])

    st.markdown("---")
    st.subheader("📋 Goals vs Actuals")
    achieved = sum([
        1 if goals['revenue']['current'] >= rev_target else 0,
        1 if goals['profit_margin']['current'] >= margin_target else 0,
        1 if goals['customers']['current'] >= cust_target else 0,
        0 if roas_unavailable else (1 if goals['roas']['current'] >= roas_target else 0)
    ])
    total_goals = 4 if not roas_unavailable else 3
    st.info(f"You're on track with **{achieved}/{total_goals}** goals. Keep pushing!")
    
    # Gap summary
    gaps = []
    if goals['revenue']['current'] < rev_target:
        gaps.append(f"Revenue: {format_currency(rev_target - goals['revenue']['current'])} to go")
    if goals['profit_margin']['current'] < margin_target:
        gaps.append(f"Margin: {margin_target - goals['profit_margin']['current']:.1f} pts to go")
    if goals['customers']['current'] < cust_target:
        gaps.append(f"Customers: {int(cust_target - goals['customers']['current']):,} to go")
    if not roas_unavailable and goals['roas']['current'] < roas_target:
        gaps.append(f"ROAS: {roas_target - goals['roas']['current']:.1f}x to go")
    if gaps:
        st.caption("Gaps: " + " | ".join(gaps))

    # Sync goal targets from inputs back to session state (for persistence)
    st.session_state.goals['revenue']['target'] = rev_target
    st.session_state.goals['profit_margin']['target'] = margin_target
    st.session_state.goals['customers']['target'] = cust_target
    st.session_state.goals['roas']['target'] = roas_target
