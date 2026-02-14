"""Executive Briefing - 30-second business health view for busy owners."""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from utils import calculate_business_health_score, calculate_key_metrics, get_change_explanation, get_metric_alerts
from utils.data_patterns import analyze_data_patterns
from utils.industry_utils import get_industry_benchmarks


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


def get_top_opportunities(data: pd.DataFrame, metrics: Dict, kpis: Dict, patterns: Dict = None) -> list:
    """Identify top opportunities from data and detected patterns."""
    opportunities = []
    patterns = patterns or {}

    # Pattern-based: dimension shifts (channel, category, product - whatever exists in data)
    dim_shifts = patterns.get('dimension_shifts', []) or patterns.get('channel_shifts', [])
    growing = [c for c in dim_shifts if c.get('change_pct', 0) > 15]
    declining = [c for c in dim_shifts if c.get('change_pct', 0) < -15]
    if growing and not declining:
        s = growing[0]
        name = s.get('segment_name') or s.get('channel', '')
        if name:
            opportunities.append({
                'title': f'Scale {name} — Up {s["change_pct"]:.0f}%',
                'impact': f'{name} grew {s["change_pct"]:.0f}% vs prior 30 days and is now {s["share_now"]:.0f}% of revenue.',
                'priority': 'high',
                'action': f'Increase investment in {name} — it\'s your growth driver'
            })
    elif declining:
        s = declining[0]
        name = s.get('segment_name') or s.get('channel', '')
        if name:
            opportunities.append({
                'title': f'Address {name} Decline',
                'impact': f'{name} down {abs(s["change_pct"]):.0f}% vs prior period.',
                'priority': 'high',
                'action': f'Review what changed in {name} — pricing, inventory, or competition'
            })

    # Pattern-based: seasonality (specific)
    seasonality = patterns.get('seasonality', [])
    peak = next((s for s in seasonality if s.get('direction') == 'above'), None)
    if peak and len(opportunities) < 3:
        opportunities.append({
            'title': f'Plan for {peak["period"]} Peak',
            'impact': peak['message'],
            'priority': 'medium',
            'action': f'Stock inventory and staff for next {peak["period"]} — historically {peak["multiplier"]}x your average'
        })

    # Pattern-based: low-margin winners (specific)
    low_margin = patterns.get('low_margin_winners', [])
    if low_margin and len(opportunities) < 3:
        lm = low_margin[0]
        opportunities.append({
            'title': f'Improve Margin on {lm["category"]}',
            'impact': lm['message'],
            'priority': 'high',
            'action': f'Raise prices or reduce costs on {lm["category"]} — high volume, thin margin'
        })

    # Fallback: metric-based (when no dimension patterns - use generic language)
    if len(opportunities) < 2:
        rev_growth = metrics.get('revenue_growth', 0)
        if rev_growth < 10 and rev_growth >= 0:
            opportunities.append({
                'title': 'Accelerate Revenue Growth',
                'impact': f'Your {rev_growth:.1f}% growth is below 10% target.',
                'priority': 'high',
                'action': 'Review what\'s driving revenue and increase investment there'
            })
        elif rev_growth < 0:
            opportunities.append({
                'title': 'Reverse Revenue Decline',
                'impact': f'Revenue down {abs(rev_growth):.1f}%. Immediate attention needed.',
                'priority': 'critical',
                'action': 'Audit churn drivers and customer acquisition'
            })

        margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
        if margin < 30 and not any('margin' in o['title'].lower() for o in opportunities):
            opportunities.append({
                'title': 'Improve Profit Margins',
                'impact': f'At {margin:.1f}%, target 35%+',
                'priority': 'high',
                'action': 'Review pricing and cost structure'
            })

        roas = data['roas'].mean() if 'roas' in data.columns else 3
        if roas < 4 and len(opportunities) < 3:
            opportunities.append({
                'title': 'Optimize Marketing ROI',
                'impact': f'ROAS of {roas:.1f}x is below 4x benchmark.',
                'priority': 'medium',
                'action': 'Pause underperformers, scale winners'
            })

    return opportunities[:3]


def get_top_risks(data: pd.DataFrame, cash_metrics: Dict, metrics: Dict, patterns: Dict = None) -> list:
    """Identify top 3 risks from data and patterns."""
    risks = []
    patterns = patterns or {}

    # Pattern-based: revenue anomalies (specific)
    anomalies = patterns.get('anomalies', [])
    drops = [a for a in anomalies if a.get('type') == 'drop']
    if drops:
        a = drops[0]
        risks.append({
            'title': f'Revenue Drop on {a["date"]}',
            'severity': 'high',
            'detail': a['message']
        })

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
    """Render the Executive Briefing - 30-second view. Leads with what to do today."""
    st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    st.title("📋 Executive Briefing")
    st.caption("Your business at a glance — 30 seconds")
    
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
    pattern_analysis = analyze_data_patterns(data)
    patterns = pattern_analysis.get('patterns', {}) if pattern_analysis.get('has_data') else {}
    opportunities = get_top_opportunities(data, metrics, kpis, patterns)
    risks = get_top_risks(data, cash_metrics, metrics, patterns)
    this_week = get_this_week_action(opportunities, risks)
    
    # === HERO: Do This Week (lead with action) ===
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#059669 0%,#047857 100%);border-radius:16px;padding:32px 36px;margin:0 0 2rem 0;border:1px solid rgba(16,185,129,0.5);box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);">
        <p style="color:rgba(255,255,255,0.9);font-size:11px;margin:0 0 10px 0;text-transform:uppercase;letter-spacing:1px;">📌 Do This Week</p>
        <p style="color:white;font-size:1.4rem;font-weight:700;margin:0;line-height:1.5;">{this_week}</p>
        <p style="color:rgba(255,255,255,0.85);font-size:0.9rem;margin:1rem 0 0 0;">Based on your data — revenue, margins, and trends.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # === Quick: Money In vs Out (cash flow at a glance) ===
    inflow = cash_metrics.get('monthly_inflow', 0)
    burn = cash_metrics.get('monthly_burn', 0)
    outflow = inflow + burn  # expenses = revenue + burn (burn is expenses - revenue)
    cf_col1, cf_col2, cf_col3 = st.columns(3)
    with cf_col1:
        st.metric("💰 Money In", format_currency(inflow), "Avg monthly revenue")
    with cf_col2:
        st.metric("💸 Money Out", format_currency(outflow), "Est. expenses")
    with cf_col3:
        surplus = inflow - outflow
        st.metric("📊 Net Cash Flow", format_currency(surplus), "Surplus" if surplus >= 0 else "Deficit")
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # === HERO: Health Score + Cash Flow ===
    col1, col2, col3 = st.columns([1, 1, 1])
    runway = cash_metrics.get('runway_months', 12)
    health_emoji = {'healthy': '🟢', 'moderate': '🟡', 'caution': '🟠', 'critical': '🔴'}.get(cash_metrics.get('cash_health', 'moderate'), '🟡')
    
    with col1:
        st.markdown(f"""
        <div style="text-align:center;padding:28px 24px;background:linear-gradient(135deg,#2563EB 0%,#1D4ED8 100%);border-radius:16px;border:1px solid rgba(59,130,246,0.5);box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);">
            <h2 style="color:white;margin:0;font-size:2.5rem;font-weight:700;">{health_score['score']}</h2>
            <p style="color:rgba(255,255,255,0.9);margin:4px 0 0 0;">{health_score['status']}</p>
            <p style="color:rgba(255,255,255,0.8);font-size:14px;">Business Health</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align:center;padding:28px 24px;background:#1f2937;border-radius:16px;border:1px solid #374151;box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);">
            <h2 style="color:white;margin:0;font-size:2rem;font-weight:700;">{health_emoji} {runway:.0f}+ mo</h2>
            <p style="color:#9ca3af;margin:8px 0 0 0;">Cash Runway</p>
            <p style="color:#6b7280;font-size:0.75rem;margin-top:6px;">Est. reserve ÷ burn</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        monthly_rev = cash_metrics.get('monthly_inflow', 0)
        st.markdown(f"""
        <div style="text-align:center;padding:28px 24px;background:#1f2937;border-radius:16px;border:1px solid #374151;box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);">
            <h2 style="color:white;margin:0;font-size:1.75rem;font-weight:700;">{format_currency(monthly_rev)}</h2>
            <p style="color:#9ca3af;margin:8px 0 0 0;">Avg Monthly Revenue</p>
            <p style="color:#6b7280;font-size:0.75rem;margin-top:6px;">Last 12 months</p>
        </div>
        """, unsafe_allow_html=True)
    
    # === vs Industry Benchmarks ===
    industry = st.session_state.get('industry', 'ecommerce')
    benchmarks = get_industry_benchmarks(industry)
    ind_name = {'ecommerce': 'E-commerce', 'saas': 'SaaS', 'restaurant': 'Restaurant', 'services': 'Services', 'general': 'General'}.get(industry, 'E-commerce')
    your_margin = float(data['profit_margin'].mean()) if 'profit_margin' in data.columns else 40
    your_roas = float(data['roas'].mean()) if 'roas' in data.columns else 3
    bench_margin = benchmarks.get('profit_margin', 35)
    bench_roas = benchmarks.get('roas', 4)
    m_vs = "above" if your_margin >= bench_margin else "below"
    r_vs = "above" if your_roas >= bench_roas else "below"
    st.markdown(f"**📊 vs {ind_name} benchmark:** Margin {your_margin:.0f}% ({m_vs} {bench_margin}% avg) · ROAS {your_roas:.1f}x ({r_vs} {bench_roas}x avg)")
    
    st.markdown("---")
    
    # === Alerts when metrics deteriorate ===
    metric_alerts = get_metric_alerts(data, metrics)
    if metric_alerts:
        st.subheader("⚠️ Alerts")
        for a in metric_alerts[:3]:
            if a['severity'] == 'critical':
                st.error(f"**{a['title']}** — {a['message']}")
            else:
                st.warning(f"**{a['title']}** — {a['message']}")
        st.markdown("---")
    
    # === Key Patterns (collapsible) ===
    dim_shifts = patterns.get('dimension_shifts', []) or patterns.get('channel_shifts', [])
    if patterns and (dim_shifts or patterns.get('seasonality') or patterns.get('top_categories')):
        with st.expander("📊 Patterns in Your Data", expanded=False):
            st.caption("Detected from your actual numbers — no generic templates.")
            if dim_shifts:
                for c in dim_shifts[:3]:
                    name = c.get('segment_name') or c.get('channel', '')
                    if name:
                        st.markdown(f"- **{name}**: {c['message']}")
            if patterns.get('seasonality'):
                for s in patterns['seasonality'][:2]:
                    st.markdown(f"- **{s['period']}**: {s['message']}")
            if patterns.get('top_categories') and not patterns.get('channel_shifts'):
                for cat in patterns['top_categories'][:3]:
                    st.markdown(f"- **{cat['category']}**: {cat['message']}")

    # === What Changed and Why (collapsible) ===
    change_explanation = get_change_explanation(data)
    if change_explanation.get('has_explanation') or change_explanation.get('summary'):
        with st.expander("📈 What Changed and Why", expanded=False):
            st.caption("Echolon identifies the underlying drivers so you don't have to investigate manually.")
            if change_explanation.get('summary'):
                st.info(change_explanation['summary'])
            for d in change_explanation.get('drivers', [])[:4]:
                st.markdown(f"- {d['explanation']}")
    
    # === Top Opportunities (with "why") ===
    st.subheader("🎯 Top Opportunities")
    for opp in opportunities:
        with st.container(border=True):
            col_l, col_r = st.columns([4, 1])
            with col_l:
                st.markdown(f"**{opp['title']}**")
                st.caption(f"**Why:** {opp['impact']}")
                st.markdown(f"*→ {opp['action']}*")
            with col_r:
                st.metric("Priority", opp['priority'].title(), "")
    
    # === Top Risks ===
    if risks:
        st.subheader("⚠️ Top Risks")
        for risk in risks:
            st.warning(f"**{risk['title']}** — {risk['detail']}")
    
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
