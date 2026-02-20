"""Executive Briefing - 30-second business health view for busy owners."""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from utils import (
    calculate_business_health_score,
    calculate_key_metrics,
    get_change_explanation,
    get_metric_alerts,
    calculate_data_confidence,
    calculate_period_diff,
    annualize_dollar_impact,
)
from utils.data_patterns import analyze_data_patterns
from utils.industry_utils import get_industry_benchmarks


def compute_cash_flow_metrics(data: pd.DataFrame) -> Dict[str, Any]:
    """Compute cash flow and runway from business data. Uses actual cost/ad_spend when available."""
    if data is None or data.empty:
        return {'runway_months': 0, 'monthly_burn': 0, 'monthly_inflow': 0, 'cash_health': 'unknown'}
    
    # Use actual date span to compute monthly revenue (not hardcoded 12)
    total_revenue = data['revenue'].sum()
    date_range_label = "Last 12 months"
    if 'date' in data.columns and len(data) >= 1:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        date_range_days = (df['date'].max() - df['date'].min()).days
        unique_months = df['date'].dt.to_period('M').nunique()
        # For monthly aggregate data (few rows per month), use unique months; else days/30.44
        if unique_months >= 2 and len(df) / max(1, unique_months) <= 31:
            num_months = float(unique_months)
        else:
            num_months = max(0.25, date_range_days / 30.44)
        monthly_revenue = total_revenue / num_months
        if num_months >= 11.5:
            date_range_label = "Last 12 months"
        elif num_months >= 5.5:
            date_range_label = f"Last {int(round(num_months))} months"
        else:
            date_range_label = f"Last {date_range_days} days"
    else:
        monthly_revenue = data['revenue'].mean() * 30 if len(data) > 0 else 0
        num_months = 12.0
        date_range_label = "Last 12 months"
    
    # Use ACTUAL cost and marketing spend when available (not estimates)
    mkt_col = 'marketing_spend' if 'marketing_spend' in data.columns else (
        'ad_spend' if 'ad_spend' in data.columns else 'marketing_cost' if 'marketing_cost' in data.columns else None)
    if mkt_col and data[mkt_col].sum() > 0:
        monthly_marketing = data[mkt_col].sum() / num_months
    else:
        monthly_marketing = monthly_revenue * 0.15  # Estimate only when missing
    
    cost_missing = 'cost' not in data.columns
    if not cost_missing:
        monthly_cost = data['cost'].sum() / num_months
        monthly_profit = monthly_revenue - (monthly_cost + monthly_marketing)
    else:
        monthly_cost = None
        monthly_profit = None  # N/A when cost missing

    # Use actual cost + ad spend when available; when cost missing, expenses = ad spend only
    monthly_expenses = (monthly_cost or 0) + monthly_marketing
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
    
    has_actual_expenses = 'cost' in data.columns or mkt_col
    return {
        'runway_months': min(runway_months, 24),
        'monthly_burn': monthly_burn,
        'monthly_inflow': monthly_inflow,
        'monthly_profit': monthly_profit,
        'cost_missing': cost_missing,
        'monthly_expenses': monthly_expenses,
        'cash_health': cash_health,
        'cash_reserve_est': cash_reserve,
        'date_range_label': date_range_label,
        'expenses_label': 'Cost + Ad Spend' if has_actual_expenses else ('Ad Spend only (cost missing)' if cost_missing and mkt_col else 'Est. expenses')
    }


def get_top_opportunities(data: pd.DataFrame, metrics: Dict, kpis: Dict, patterns: Dict = None) -> list:
    """Identify top opportunities from data and detected patterns."""
    opportunities = []
    patterns = patterns or {}

    # Pattern-based: dimension shifts — sort by dollar_impact first (not % growth)
    # Filter: minimum dollar impact to avoid "Up 32% but added $0" contradictions
    dim_shifts = patterns.get('dimension_shifts', []) or patterns.get('channel_shifts', [])
    growing = sorted(
        [c for c in dim_shifts if c.get('change_pct', 0) > 15 and c.get('current_rev', 0) > 0],
        key=lambda x: -x.get('dollar_impact', 0)
    )
    declining = sorted([c for c in dim_shifts if c.get('change_pct', 0) < -15], key=lambda x: -abs(x.get('dollar_impact', 0)))
    if growing and not declining:
        s = growing[0]
        name = s.get('segment_name') or s.get('channel', '')
        dollar_impact = s.get('dollar_impact', 0)
        if name:
            # Consistent "why": show dollar impact when meaningful; else describe share shift
            if dollar_impact and abs(dollar_impact) >= 100:
                impact_msg = f'{name} added ~${dollar_impact:,.0f} vs prior period and is now {s["share_now"]:.0f}% of revenue.'
            else:
                impact_msg = f'{name} grew to {s["share_now"]:.0f}% of revenue (share shift vs prior period).'
            opportunities.append({
                'title': f'Scale {name} — Up {s["change_pct"]:.0f}%',
                'impact': impact_msg,
                'priority': 'high',
                'action': f'Increase investment in {name} — highest dollar impact' if dollar_impact and abs(dollar_impact) >= 100 else f'Increase investment in {name} — growing share',
                'dollar_impact': dollar_impact
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

    # Fallback: use top products/categories when available (even without shifts)
    if len(opportunities) < 2:
        top_products = patterns.get('top_products', [])
        top_categories = patterns.get('top_categories', [])
        if top_products and not any('product' in str(o.get('title', '')).lower() for o in opportunities):
            p = top_products[0]
            opportunities.append({
                'title': f'Optimize {p["product"]}',
                'impact': f'{p["product"]} is {p["share"]:.0f}% of revenue.',
                'priority': 'medium',
                'action': f'Review pricing and promotion on {p["product"]} — your top seller'
            })
        elif top_categories and len(opportunities) < 2:
            c = top_categories[0]
            opportunities.append({
                'title': f'Focus on {c["category"]}',
                'impact': f'{c["category"]} drives {c["share"]:.0f}% of revenue.',
                'priority': 'medium',
                'action': f'Scale {c["category"]} — your largest category'
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

        roas = kpis.get('roas') if kpis else (data['roas'].mean() if 'roas' in data.columns else None)
        if roas is not None and roas < 4 and len(opportunities) < 3 and not kpis.get('roas_unavailable'):
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


def get_this_week_action(opportunities: list, risks: list, patterns: dict = None) -> str:
    """Recommend single action for the week. Uses product/category names when available."""
    if risks and risks[0].get('severity') == 'critical':
        return risks[0]['detail']
    if opportunities:
        return opportunities[0]['action']
    # Fallback: use top product/category if available
    patterns = patterns or {}
    top_products = patterns.get('top_products', [])
    top_categories = patterns.get('top_categories', [])
    if top_products:
        return f"Review {top_products[0]['product']} — your top seller ({top_products[0]['share']:.0f}% of revenue)"
    if top_categories:
        return f"Focus on {top_categories[0]['category']} — your largest category ({top_categories[0]['share']:.0f}% of revenue)"
    return "Review key metrics and plan next quarter's priorities."


def render_executive_briefing_page(data, kpis, format_currency, format_percentage, format_multiplier):
    """Render the Executive Briefing - 30-second view. Leads with what to do today."""
    st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    st.title("📋 Executive Briefing")
    st.caption("Your business at a glance — 30 seconds")
    
    # Window subtitle (all metrics use this window)
    winfo = kpis.get('window_info', {})
    if winfo.get('label'):
        st.caption(f"**Window:** {winfo['label']}")
    
    # ROAS unavailable warning
    if kpis.get('roas_unavailable'):
        st.warning("⚠️ **ROAS unavailable:** Map `ad_spend` or `marketing_spend` in Data Sources to see ROAS. No placeholder used.")
    
    # Compute metrics
    metrics = calculate_key_metrics(data)
    winfo = kpis.get('window_info', {})
    period_days = winfo.get('days', 90) // 2  # half-period for H1 vs H2
    roas_val = kpis.get('roas')
    health_metrics = {
        'revenue_growth': metrics.get('revenue_growth', 0),
        'profit_margin': metrics.get('profit_margin'),  # None when cost missing
        'cash_flow_ratio': 1.2,
        'customer_growth': metrics.get('customer_growth', 0),
    }
    if roas_val is not None:
        health_metrics['roas'] = roas_val
    health_score = calculate_business_health_score(health_metrics)
    cash_metrics = compute_cash_flow_metrics(data)
    pattern_analysis = analyze_data_patterns(data)
    patterns = pattern_analysis.get('patterns', {}) if pattern_analysis.get('has_data') else {}
    opportunities = get_top_opportunities(data, metrics, kpis, patterns)
    risks = get_top_risks(data, cash_metrics, metrics, patterns)
    this_week = get_this_week_action(opportunities, risks, patterns)
    
    # === HERO: Do This Week (lead with action) ===
    st.markdown(f"""
    <div style="font-family:'DM Sans',sans-serif;background:linear-gradient(135deg,#059669 0%,#047857 100%);border-radius:20px;padding:2rem 2.25rem;margin:0 0 2rem 0;border:1px solid rgba(52,211,153,0.4);box-shadow:0 10px 40px -10px rgba(5,150,105,0.4);">
        <p style="color:rgba(255,255,255,0.9);font-size:10px;margin:0 0 12px 0;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;">Do This Week</p>
        <p style="color:white;font-size:1.5rem;font-weight:700;margin:0;line-height:1.5;letter-spacing:-0.01em;">{this_week}</p>
        <p style="color:rgba(255,255,255,0.8);font-size:0.9rem;margin:1.25rem 0 0 0;">Based on your data — revenue, margins, and trends.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # === Money In/Out (primary — must balance: surplus = inflow - outflow) ===
    inflow = cash_metrics.get('monthly_inflow', 0)
    outflow = cash_metrics.get('monthly_expenses', 0)  # avg monthly cost + ad spend
    surplus = inflow - outflow  # explicit: Net Cash Flow = Money In - Money Out
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem;">
        <div style="background:linear-gradient(135deg,#059669 0%,#047857 100%);padding:1.75rem;border-radius:16px;text-align:center;border:1px solid rgba(52,211,153,0.4);">
            <p style="color:rgba(255,255,255,0.9);font-size:0.75rem;margin:0 0 8px 0;text-transform:uppercase;">Money In</p>
            <p style="color:white;font-size:1.75rem;font-weight:700;margin:0;">{format_currency(inflow)}</p>
            <p style="color:rgba(255,255,255,0.8);font-size:0.8rem;margin:8px 0 0 0;">Avg monthly revenue</p>
        </div>
        <div style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);padding:1.75rem;border-radius:16px;text-align:center;border:1px solid #374151;">
            <p style="color:#94a3b8;font-size:0.75rem;margin:0 0 8px 0;text-transform:uppercase;">Money Out</p>
            <p style="color:white;font-size:1.75rem;font-weight:700;margin:0;">{format_currency(outflow)}</p>
            <p style="color:#94a3b8;font-size:0.8rem;margin:8px 0 0 0;font-style:italic;">{cash_metrics.get('expenses_label', 'Est. expenses')} · Avg monthly</p>
        </div>
        <div style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);padding:1.75rem;border-radius:16px;text-align:center;border:1px solid #374151;">
            <p style="color:#94a3b8;font-size:0.75rem;margin:0 0 8px 0;text-transform:uppercase;">Net Cash Flow</p>
            <p style="color:white;font-size:1.75rem;font-weight:700;margin:0;">{format_currency(surplus)}</p>
            <p style="color:#64748b;font-size:0.8rem;margin:8px 0 0 0;">{"Surplus" if surplus >= 0 else "Deficit"}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    from components import display_explain_this_number
    display_explain_this_number(
        "Net Cash Flow",
        "Revenue − (Cost + Ad Spend)",
        winfo.get('label', 'Last 90 Days'),
        "Ops Overhead: 0% (not assumed)" if not ('cost' in data.columns and ('marketing_spend' in data.columns or 'ad_spend' in data.columns)) else "Using measured cost and ad spend.",
        aggregation="SUM over rows in window"
    )
    
    # === Data Confidence (next to Business Health) ===
    data_conf = calculate_data_confidence(data, kpis, winfo)
    conf_level = data_conf.get('level', 'High')
    conf_color = {'High': '#10B981', 'Medium': '#F59E0B', 'Low': '#EF4444'}.get(conf_level, '#94a3b8')

    # === Health Score (secondary) + Data Confidence ===
    col1, col2, col3 = st.columns([1, 1, 1])
    runway = cash_metrics.get('runway_months', 12)
    health_emoji = {'healthy': '🟢', 'moderate': '🟡', 'caution': '🟠', 'critical': '🔴'}.get(cash_metrics.get('cash_health', 'moderate'), '🟡')

    with col1:
        st.markdown(f"""
        <div style="text-align:center;padding:28px 24px;background:linear-gradient(135deg,#2563EB 0%,#1D4ED8 100%);border-radius:16px;border:1px solid rgba(59,130,246,0.5);box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);">
            <h2 style="color:white;margin:0;font-size:2.5rem;font-weight:700;">{health_score['score']}</h2>
            <p style="color:rgba(255,255,255,0.9);margin:4px 0 0 0;">{health_score['status']}</p>
            <p style="color:rgba(255,255,255,0.8);font-size:14px;">Business Health</p>
            <p style="color:{conf_color};font-size:12px;margin-top:10px;font-weight:600;">Data Confidence: {conf_level}</p>
        </div>
        """, unsafe_allow_html=True)
        display_explain_this_number(
            "Business Health Score",
            "Weighted: Revenue, Profitability, Cash Flow, Customer Growth, Efficiency (ROAS). 0–100 scale.",
            winfo.get('label', '—'),
            "Components: " + ", ".join(f"{k}={v}" for k, v in (health_score.get('breakdown') or {}).items() if v is not None),
            aggregation="Component scores aggregated by weighted average"
        )
    
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
            <p style="color:#6b7280;font-size:0.75rem;margin-top:6px;">{cash_metrics.get('date_range_label', 'Last 12 months')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # === vs Industry Benchmarks ===
    industry = st.session_state.get('industry', 'ecommerce')
    benchmarks = get_industry_benchmarks(industry)
    ind_name = {'ecommerce': 'E-commerce', 'saas': 'SaaS', 'restaurant': 'Restaurant', 'services': 'Services', 'general': 'General'}.get(industry, 'E-commerce')
    your_margin = kpis.get('profit_margin')
    your_roas = kpis.get('roas')
    bench_margin = benchmarks.get('profit_margin', 35)
    bench_roas = benchmarks.get('roas', 4)
    if your_margin is not None:
        m_vs = "above" if your_margin >= bench_margin else "below"
        margin_line = f"Margin {your_margin:.0f}% ({m_vs} {bench_margin}% avg)"
    else:
        margin_line = "Margin N/A (cost missing)"
    if kpis.get('roas_unavailable') or your_roas is None:
        roas_line = "ROAS N/A (map ad_spend)"
    else:
        r_vs = "above" if your_roas >= bench_roas else "below"
        roas_line = f"ROAS {your_roas:.1f}x ({r_vs} {bench_roas}x avg)"
    margin_def = kpis.get('margin_definition', 'Gross')
    st.markdown(f"**📊 vs {ind_name} benchmark:** {margin_line} · {roas_line}")
    st.caption(f"Margin = {margin_def} (revenue − cost)")
    # Explain ROAS (when available) and Margin
    with st.expander("📖 Explain: ROAS & Margin", expanded=False):
        st.markdown("**ROAS** = SUM(revenue) ÷ SUM(marketing_spend or ad_spend)")
        st.markdown(f"**Window:** {winfo.get('label', '—')}")
        st.markdown(f"**Margin:** {kpis.get('margin_definition', 'Gross')} = (revenue − cost) ÷ revenue")
        if kpis.get('roas_unavailable'):
            st.caption("ROAS unavailable — map ad_spend or marketing_spend in Data Sources.")
    
    # === What Changed? Diff Panel (period-over-period) ===
    period_diff = calculate_period_diff(data, kpis, format_currency)
    if period_diff.get('has_data') and period_diff.get('changes'):
        st.markdown("#### 📈 Since last period")
        diff_cols = st.columns(min(4, len(period_diff['changes'])))
        for i, ch in enumerate(period_diff['changes'][:4]):
            with diff_cols[i]:
                st.metric(ch['metric'], ch['fmt'], "")
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
                        msg = c['message']
                        di = c.get('dollar_impact', 0)
                        if di and period_days > 0:
                            ann = annualize_dollar_impact(di, period_days)
                            msg += f" (+{format_currency(ann)} annualized)"
                        st.markdown(f"- **{name}**: {msg}")
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
    
    # === Top Opportunities (with dollar impact, "why", and contextual links) ===
    OPP_TO_PAGE = {'Scale': 'Analytics', 'Address': 'Insights', 'Plan for': 'Predictions', 'Improve Margin': 'Margin Analysis',
                   'Improve Profit': 'Margin Analysis', 'Optimize': 'Analytics', 'Focus on': 'Analytics',
                   'Accelerate Revenue': 'Predictions', 'Reverse Revenue': 'Insights', 'Optimize Marketing': 'Analytics'}
    st.subheader("🎯 Top Opportunities")
    for i, opp in enumerate(opportunities):
        with st.container(border=True):
            col_l, col_r = st.columns([4, 1])
            with col_l:
                title_line = opp['title']
                dollar_impact = opp.get('dollar_impact', 0)
                if dollar_impact and period_days > 0:
                    ann = annualize_dollar_impact(dollar_impact, period_days)
                    title_line += f" (+{format_currency(ann)} annualized)"
                st.markdown(f"**{title_line}**")
                st.caption(f"**Why:** {opp['impact']}")
                st.markdown(f"*→ {opp['action']}*")
                link_page = next((p for k, p in OPP_TO_PAGE.items() if opp['title'].startswith(k)), None)
                if link_page:
                    if st.button(f"→ Go to {link_page}", key=f"opp_link_{i}_{link_page}"):
                        st.session_state.current_page = link_page
                        st.rerun()
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
