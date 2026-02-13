"""Executive Briefing - 30-second business health view for busy owners."""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from utils import calculate_business_health_score, calculate_key_metrics


def compute_cash_flow_metrics(data: pd.DataFrame) -> Dict[str, Any]:
    """Compute cash flow and runway from business data."""
    if data is None or data.empty:
        return {'runway_months': 0, 'monthly_burn': 0, 'monthly_inflow': 0, 'cash_health': 'unknown'}
    
    # Estimate: revenue = inflow, expenses = revenue * (1 - margin) + marketing
    monthly_revenue = data['revenue'].sum() / 12 if len(data) >= 30 else data['revenue'].mean() * 30
    monthly_marketing = data['marketing_spend'].mean() * 30 if 'marketing_spend' in data.columns else monthly_revenue * 0.15
    margin = data['profit_margin'].mean() / 100 if 'profit_margin' in data.columns else 0.4
    monthly_profit = monthly_revenue * margin
    monthly_cogs = monthly_revenue * (1 - margin)
    monthly_expenses = monthly_cogs + monthly_marketing + (monthly_revenue * 0.2)  # + 20% ops
    monthly_inflow = monthly_revenue
    monthly_burn = monthly_expenses - monthly_revenue  # Negative = profitable
    
    # Runway: assume 3 months cash reserve (simplified)
    cash_reserve = monthly_revenue * 3  # Typical SMB buffer
    if monthly_burn > 0:
        runway_months = cash_reserve / monthly_burn if monthly_burn > 0 else 24
    else:
        runway_months = 24  # Profitable = indefinite runway
    
    if runway_months >= 12:
        cash_health = 'healthy'
    elif runway_months >= 6:
        cash_health = 'moderate'
    elif runway_months >= 3:
        cash_health = 'caution'
    else:
        cash_health = 'critical'
    
    return {
        'runway_months': min(runway_months, 24),
        'monthly_burn': monthly_burn,
        'monthly_inflow': monthly_inflow,
        'monthly_profit': monthly_profit,
        'cash_health': cash_health,
        'cash_reserve_est': cash_reserve
    }


def get_top_opportunities(data: pd.DataFrame, metrics: Dict, kpis: Dict) -> list:
    """Identify top 3 opportunities from data."""
    opportunities = []
    
    # Revenue growth opportunity
    rev_growth = metrics.get('revenue_growth', 0)
    if rev_growth < 10 and rev_growth >= 0:
        opportunities.append({
            'title': 'Accelerate Revenue Growth',
            'impact': f'Your {rev_growth:.1f}% growth is below 10% target. Marketing optimization could add 5-15%',
            'priority': 'high',
            'action': 'Review top-performing channels and increase spend'
        })
    elif rev_growth < 0:
        opportunities.append({
            'title': 'Reverse Revenue Decline',
            'impact': f'Revenue down {abs(rev_growth):.1f}%. Immediate attention needed.',
            'priority': 'critical',
            'action': 'Audit churn drivers and customer acquisition'
        })
    
    # Margin opportunity
    margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
    if margin < 30:
        opportunities.append({
            'title': 'Improve Profit Margins',
            'impact': f'At {margin:.1f}%, you\'re leaving money on the table. Target 35%+',
            'priority': 'high',
            'action': 'Review pricing and cost structure'
        })
    
    # ROAS opportunity
    roas = data['roas'].mean() if 'roas' in data.columns else 3
    if roas < 4:
        opportunities.append({
            'title': 'Optimize Marketing ROI',
            'impact': f'ROAS of {roas:.1f}x is below 4x benchmark. Reallocate ad spend.',
            'priority': 'medium',
            'action': 'Pause underperformers, scale winners'
        })
    
    # Customer growth
    cust_growth = metrics.get('customer_growth', 0)
    if cust_growth < 5 and 'customers' in data.columns:
        opportunities.append({
            'title': 'Boost Customer Acquisition',
            'impact': f'Customer growth at {cust_growth:.1f}%. Room to scale.',
            'priority': 'medium',
            'action': 'Test new acquisition channels'
        })
    
    return opportunities[:3]


def get_top_risks(data: pd.DataFrame, cash_metrics: Dict, metrics: Dict) -> list:
    """Identify top 3 risks from data."""
    risks = []
    
    if cash_metrics.get('cash_health') == 'critical':
        risks.append({
            'title': 'Low Cash Runway',
            'severity': 'critical',
            'detail': f'Estimated runway under 3 months. Prioritize collections and cost reduction.'
        })
    elif cash_metrics.get('cash_health') == 'caution':
        risks.append({
            'title': 'Cash Runway Declining',
            'severity': 'high',
            'detail': f'~{cash_metrics.get("runway_months", 0):.0f} months runway. Build reserves.'
        })
    
    rev_growth = metrics.get('revenue_growth', 0)
    if rev_growth < -5:
        risks.append({
            'title': 'Revenue Decline',
            'severity': 'high',
            'detail': f'Revenue down {abs(rev_growth):.1f}% vs prior period.'
        })
    
    if 'profit_margin' in data.columns and data['profit_margin'].mean() < 15:
        risks.append({
            'title': 'Thin Margins',
            'severity': 'medium',
            'detail': 'Profit margin may be unsustainable. Review pricing.'
        })
    
    return risks[:3]


def get_this_week_action(opportunities: list, risks: list) -> str:
    """Recommend single action for the week."""
    if risks and risks[0].get('severity') == 'critical':
        return risks[0]['detail']
    if opportunities:
        return opportunities[0]['action']
    return "Review key metrics and plan next quarter's priorities."


def render_executive_briefing_page(data, kpis, format_currency, format_percentage, format_multiplier):
    """Render the Executive Briefing - 30-second view."""
    st.title("📋 Executive Briefing")
    st.markdown("### Your business at a glance — *30 seconds*")
    
    # Compute metrics
    metrics = calculate_key_metrics(data)
    health_metrics = {
        'revenue_growth': metrics.get('revenue_growth', 0),
        'profit_margin': float(data['profit_margin'].mean()) if 'profit_margin' in data.columns else 40,
        'cash_flow_ratio': 1.2,
        'customer_growth': metrics.get('customer_growth', 0),
        'roas': float(data['roas'].mean()) if 'roas' in data.columns else 3
    }
    health_score = calculate_business_health_score(health_metrics)
    cash_metrics = compute_cash_flow_metrics(data)
    opportunities = get_top_opportunities(data, metrics, kpis)
    risks = get_top_risks(data, cash_metrics, metrics)
    this_week = get_this_week_action(opportunities, risks)
    
    # === HERO: Health Score + Cash Flow ===
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="text-align:center;padding:24px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:16px;">
            <h2 style="color:white;margin:0;font-size:48px;">{health_score['score']}</h2>
            <p style="color:rgba(255,255,255,0.9);margin:4px 0 0 0;">{health_score['status']}</p>
            <p style="color:rgba(255,255,255,0.8);font-size:14px;">Business Health</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        runway = cash_metrics.get('runway_months', 12)
        health_emoji = {'healthy': '🟢', 'moderate': '🟡', 'caution': '🟠', 'critical': '🔴'}.get(cash_metrics.get('cash_health', 'moderate'), '🟡')
        st.markdown(f"""
        <div style="text-align:center;padding:24px;background:#1f2937;border-radius:16px;border:1px solid #374151;">
            <h2 style="color:white;margin:0;font-size:36px;">{health_emoji} {runway:.0f}+ mo</h2>
            <p style="color:#9ca3af;margin:4px 0 0 0;">Cash Runway</p>
            <p style="color:#6b7280;font-size:12px;margin-top:8px;">Est. reserve ÷ burn</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        monthly_rev = cash_metrics.get('monthly_inflow', 0)
        st.markdown(f"""
        <div style="text-align:center;padding:24px;background:#1f2937;border-radius:16px;border:1px solid #374151;">
            <h2 style="color:white;margin:0;font-size:28px;">{format_currency(monthly_rev)}</h2>
            <p style="color:#9ca3af;margin:4px 0 0 0;">Avg Monthly Revenue</p>
            <p style="color:#6b7280;font-size:12px;margin-top:8px;">Last 12 months</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === Top Opportunities ===
    st.subheader("🎯 Top Opportunities")
    for opp in opportunities:
        with st.container(border=True):
            col_l, col_r = st.columns([4, 1])
            with col_l:
                st.markdown(f"**{opp['title']}**")
                st.caption(opp['impact'])
                st.markdown(f"*→ {opp['action']}*")
            with col_r:
                st.metric("Priority", opp['priority'].title(), "")
    
    st.markdown("---")
    
    # === Top Risks ===
    if risks:
        st.subheader("⚠️ Top Risks")
        for risk in risks:
            st.warning(f"**{risk['title']}** — {risk['detail']}")
    
    st.markdown("---")
    
    # === This Week's Action ===
    st.subheader("📌 Do This Week")
    st.success(f"**{this_week}**")
    
    st.markdown("---")
    
    # === Cash Flow Detail ===
    with st.expander("💵 Cash Flow & Runway Details", expanded=False):
        st.markdown("""
        **How we estimate runway:** We use your revenue and expense patterns to estimate monthly burn. 
        Runway = assumed cash reserve ÷ monthly burn. This is directional, not a substitute for proper cash flow forecasting.
        """)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Monthly Inflow", format_currency(cash_metrics.get('monthly_inflow', 0)), "")
        with c2:
            burn = cash_metrics.get('monthly_burn', 0)
            st.metric("Monthly Burn", format_currency(abs(burn)), "Surplus" if burn < 0 else "Deficit")
        with c3:
            st.metric("Est. Cash Health", cash_metrics.get('cash_health', 'N/A').title(), "")
    
    st.markdown("---")
    st.caption(f"Briefing generated {datetime.now().strftime('%Y-%m-%d %H:%M')} | Based on your business data")
