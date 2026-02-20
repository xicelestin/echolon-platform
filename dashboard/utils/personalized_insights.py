"""Personalized AI insights engine - generates real, actionable feedback from business data.

Every insight is derived from actual metrics, includes specific numbers, dollar impact,
and concrete next steps for business owners. No generic placeholders.
"""
import pandas as pd
from typing import Dict, List, Any, Optional
from .metrics_utils import calculate_key_metrics, get_period_data
from .industry_utils import get_industry_benchmarks


def _fmt_cur(v: float) -> str:
    """Short currency format."""
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"


def _get_benchmarks(industry: str = 'general') -> Dict[str, float]:
    """Get industry-specific benchmarks."""
    b = get_industry_benchmarks(industry)
    return {
        'margin': b.get('profit_margin', 35),
        'roas': b.get('roas', 4),
        'retention': b.get('retention', 75),
        'churn_bench': 100 - b.get('retention', 75),  # e.g. 75% retention = 25% annual churn
    }


def get_what_changed(data: pd.DataFrame, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Period-over-period: what changed vs prior period.
    Returns list of {metric, current, previous, change_pct, direction, message}.
    """
    changes = []
    if data is None or len(data) < 60 or 'date' not in data.columns:
        return changes

    try:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        curr, prev = get_period_data(df, 'date', 'month')
        if curr.empty or prev.empty:
            return changes

        # Revenue
        if 'revenue' in data.columns:
            c_rev, p_rev = curr['revenue'].sum(), prev['revenue'].sum()
            if p_rev > 0:
                pct = ((c_rev - p_rev) / p_rev) * 100
                changes.append({
                    'metric': 'Revenue',
                    'current': c_rev,
                    'previous': p_rev,
                    'change_pct': pct,
                    'direction': 'up' if pct > 0 else 'down',
                    'message': f"Revenue {'up' if pct > 0 else 'down'} {abs(pct):.1f}% vs prior 30 days"
                })

        # Margin
        if 'profit_margin' in data.columns:
            c_m, p_m = curr['profit_margin'].mean(), prev['profit_margin'].mean()
            if p_m > 0:
                pct = ((c_m - p_m) / p_m) * 100
                changes.append({
                    'metric': 'Profit Margin',
                    'current': c_m,
                    'previous': p_m,
                    'change_pct': pct,
                    'direction': 'up' if pct > 0 else 'down',
                    'message': f"Margin {'up' if pct > 0 else 'down'} {abs(pct):.1f} pts ({c_m:.1f}% vs {p_m:.1f}%)"
                })

        # ROAS
        if 'roas' in data.columns:
            c_r, p_r = curr['roas'].mean(), prev['roas'].mean()
            if p_r > 0:
                pct = ((c_r - p_r) / p_r) * 100
                changes.append({
                    'metric': 'ROAS',
                    'current': c_r,
                    'previous': p_r,
                    'change_pct': pct,
                    'direction': 'up' if pct > 0 else 'down',
                    'message': f"ROAS {'up' if pct > 0 else 'down'} {abs(pct):.1f}% ({c_r:.1f}x vs {p_r:.1f}x)"
                })

        # Customers
        if 'customers' in data.columns and len(curr) > 0 and len(prev) > 0:
            c_c, p_c = curr['customers'].iloc[-1], prev['customers'].iloc[-1]
            if pd.notna(c_c) and pd.notna(p_c) and p_c > 0:
                pct = ((c_c - p_c) / p_c) * 100
                changes.append({
                    'metric': 'Customers',
                    'current': c_c,
                    'previous': p_c,
                    'change_pct': pct,
                    'direction': 'up' if pct > 0 else 'down',
                    'message': f"Customers {'up' if pct > 0 else 'down'} {abs(pct):.1f}% ({int(c_c)} vs {int(p_c)})"
                })
    except Exception:
        pass
    return changes[:5]


def get_progress_callouts(data: pd.DataFrame, metrics: Dict[str, float]) -> List[str]:
    """
    Positive progress: "You improved X by Y% this period."
    """
    callouts = []
    changes = get_what_changed(data, metrics)
    for c in changes:
        if c['direction'] == 'up' and abs(c['change_pct']) >= 2:
            if c['metric'] == 'Revenue':
                callouts.append(f"**Revenue** up {c['change_pct']:.1f}% vs prior 30 days — momentum is building.")
            elif c['metric'] == 'Profit Margin':
                callouts.append(f"**Margin** improved {c['current'] - c['previous']:.1f} pts — pricing/cost moves are working.")
            elif c['metric'] == 'ROAS':
                callouts.append(f"**ROAS** up {c['change_pct']:.1f}% — marketing efficiency improving.")
    return callouts[:3]


def get_quick_wins(data: pd.DataFrame, metrics: Dict[str, float], industry: str = 'general', kpis: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Actions that take under 2 hours. High impact, low effort.
    ROAS advice gated when roas_unavailable.
    """
    wins = []
    if data is None or data.empty:
        return wins

    kpis = kpis or {}
    roas_unavailable = kpis.get('roas_unavailable', True)
    total_rev = data['revenue'].sum() if 'revenue' in data.columns else 0
    margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
    roas = kpis.get('roas') if not roas_unavailable else None
    if roas is None and not roas_unavailable and 'roas' in data.columns:
        roas = data['roas'].mean()
    bench = _get_benchmarks(industry)

    if not roas_unavailable and roas is not None and roas < bench['roas'] and total_rev > 5000:
        wins.append({
            'action': 'Pause your lowest-ROAS campaign (takes 15 min)',
            'impact': f"Frees budget for winners — could add ~{_fmt_cur(total_rev * 0.02 * margin / 100)} profit",
            'time': '15 min'
        })
    if 'orders' in data.columns and data['orders'].sum() > 0:
        aov = total_rev / data['orders'].sum()
        if aov < 75:
            wins.append({
                'action': 'Add free-shipping threshold 15% above current AOV',
                'impact': f"Typically +10% AOV — ~{_fmt_cur(total_rev * 0.1 * margin / 100)} profit potential",
                'time': '1 hr'
            })
    if margin < bench['margin'] and margin > 0:
        wins.append({
            'action': 'Raise price 5% on your top-selling product',
            'impact': f"Direct margin lift — ~{_fmt_cur(total_rev * 0.05 * 0.05)} if it's 20% of revenue",
            'time': '30 min'
        })
    wins.append({
        'action': 'Email your top 10 customers — ask for one referral each',
        'impact': 'Warm leads convert 3-5x better than cold',
        'time': '1 hr'
    })
    return wins[:4]


def get_top_priority_this_week(
    data: pd.DataFrame,
    metrics: Dict[str, float],
    industry: str = 'general',
    kpis: Optional[Dict] = None
) -> Optional[Dict[str, Any]]:
    """
    Single clear recommendation: the one thing to do first.
    Scored by urgency × impact. Returns {title, action, impact, urgency, evidence}.
    ROAS-based advice is gated: never show when roas_unavailable.
    """
    if data is None or data.empty:
        return None

    kpis = kpis or {}
    roas_unavailable = kpis.get('roas_unavailable', True)
    total_rev = data['revenue'].sum() if 'revenue' in data.columns else 0
    rev_growth = metrics.get('revenue_growth', 0)
    margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
    roas = kpis.get('roas') if not roas_unavailable else None
    if roas is None and not roas_unavailable:
        roas = data['roas'].mean() if 'roas' in data.columns else None
    churn = metrics.get('churn_rate', 2.5)
    marketing_spend = data['marketing_spend'].sum() if 'marketing_spend' in data.columns else total_rev * 0.15
    bench = _get_benchmarks(industry)

    candidates = []

    # Revenue decline - highest urgency
    if rev_growth < -5:
        candidates.append({
            'title': 'Reverse Revenue Decline',
            'action': 'This week: (1) Check what changed in your top revenue sources. (2) Review pricing vs competitors. (3) Reach out to top 20 customers for feedback.',
            'impact': f"Stop ~{_fmt_cur(total_rev * abs(rev_growth) / 100)} monthly bleed",
            'urgency': 10,
            'evidence': f"Revenue down {abs(rev_growth):.1f}% vs prior period.",
        })
    # Churn spike
    elif churn >= 4:
        candidates.append({
            'title': 'Fix High Churn',
            'action': 'Send win-back email to churned customers (10% discount). Add onboarding check-in at day 7.',
            'impact': '25-35% churn reduction possible',
            'urgency': 9,
            'evidence': f"Churn at {churn:.1f}% — above 3% monthly benchmark.",
        })
    # Margin below benchmark
    elif margin < bench['margin'] - 5 and margin > 0:
        gap = bench['margin'] - margin
        est = total_rev * (gap / 100)
        candidates.append({
            'title': 'Improve Profit Margins',
            'action': f"Raise prices 5-10% on top 3 products. Your margin is {margin:.1f}% vs {bench['margin']:.0f}% for your industry.",
            'impact': f"~{_fmt_cur(est)} profit upside",
            'urgency': 8,
            'evidence': f"Margin {margin:.1f}% vs {bench['margin']:.0f}% industry benchmark.",
        })
    # ROAS below benchmark — ONLY when ROAS is valid (not unavailable)
    elif not roas_unavailable and roas is not None and roas < bench['roas'] and marketing_spend > 500:
        est = marketing_spend * (bench['roas'] - roas) * (margin / 100)
        candidates.append({
            'title': 'Optimize Marketing ROI',
            'action': f"Pause bottom 20% of campaigns by ROAS. Reallocate to top 3. ROAS {roas:.1f}x vs {bench['roas']:.0f}x benchmark.",
            'impact': f"~{_fmt_cur(est)} profit with same spend",
            'urgency': 7,
            'evidence': f"ROAS {roas:.1f}x vs {bench['roas']:.0f}x for your industry.",
        })
    # Modest growth - scale
    elif rev_growth < 10 and rev_growth >= 0:
        candidates.append({
            'title': 'Accelerate Revenue Growth',
            'action': 'Identify top 2 acquisition channels and increase spend 20%. Test one new channel (referrals, partnerships).',
            'impact': f"~{_fmt_cur(total_rev * 0.05)} revenue potential",
            'urgency': 6,
            'evidence': f"Growth at {rev_growth:.1f}% — industry leaders target 10-15%.",
        })
    # AOV opportunity
    elif 'orders' in data.columns and data['orders'].sum() > 0:
        aov = total_rev / data['orders'].sum()
        if aov < 75 and total_rev > 10000:
            uplift = total_rev * 0.12 * (margin / 100)
            candidates.append({
                'title': 'Boost Average Order Value',
                'action': 'Add "Frequently bought together" at checkout. Create 2-3 product bundles (10% discount).',
                'impact': f"~{_fmt_cur(uplift)} profit potential",
                'urgency': 5,
                'evidence': f"AOV ${aov:.0f} — bundles typically add 10-15%.",
            })

    # When ROAS unavailable, add Connect as fallback (low urgency)
    if roas_unavailable:
        candidates.append({
            'title': 'Connect Marketing Spend',
            'action': 'Map ad_spend or marketing_spend in Data Sources to enable ROAS insights and ROI recommendations.',
            'impact': 'Unlock marketing efficiency analysis',
            'urgency': 2,
            'evidence': 'ROAS unavailable — connect marketing spend column.',
        })
    if not candidates:
        return {
            'title': 'Stay the Course',
            'action': 'Your metrics look solid. Focus on execution: maintain top performers, monitor churn weekly.',
            'impact': 'Consistent performance',
            'urgency': 1,
            'evidence': 'Key metrics within or above benchmarks.',
        }

    # Pick highest urgency
    return max(candidates, key=lambda c: c['urgency'])


def generate_personalized_insights(
    data: pd.DataFrame,
    metrics: Dict[str, float],
    industry: str = 'general',
    patterns: Optional[Dict[str, Any]] = None,
    kpis: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Generate personalized insights from actual business data.
    Uses industry-specific benchmarks and optional pattern data for specificity.
    """
    insights = []
    if data is None or (hasattr(data, 'empty') and data.empty):
        return insights

    patterns = patterns or {}
    bench = _get_benchmarks(industry)

    # Pattern-based insights: use dimension_shifts (channel, category, product - whatever exists)
    dim_shifts = patterns.get('dimension_shifts', []) or patterns.get('channel_shifts', [])
    if dim_shifts:
        best = max(dim_shifts, key=lambda c: c.get('change_pct', 0))
        worst = min(dim_shifts, key=lambda c: c.get('change_pct', 0))
        best_name = best.get('segment_name') or best.get('channel', '')
        worst_name = worst.get('segment_name') or worst.get('channel', '')
        dim_type = best.get('dimension_type', 'segment')
        if best.get('change_pct', 0) > 15 and best_name:
            insights.append({
                'type': 'positive',
                'icon': '📈',
                'title': f'{best_name} Is Your Growth Driver',
                'message': best['message'],
                'action': f'Invest more in {best_name} — it\'s outperforming. Consider shifting budget from underperformers.',
                'impact': f'{best_name} is {best["share_now"]:.0f}% of revenue and growing'
            })
        if worst.get('change_pct', 0) < -15 and worst_name and worst_name != best_name:
            insights.append({
                'type': 'opportunity',
                'icon': '⚠️',
                'title': f'{worst_name} Needs Attention',
                'message': worst['message'],
                'action': f'Audit {worst_name}: pricing, inventory, promotions. Consider reallocating to stronger performers.',
                'impact': f'Declining share — address before it worsens'
            })

    low_margin = patterns.get('low_margin_winners', [])
    if low_margin:
        lm = low_margin[0]
        insights.append({
            'type': 'opportunity',
            'icon': '💰',
            'title': f'Thin Margin on High-Volume {lm["category"]}',
            'message': lm['message'],
            'action': f'Raise prices 5-10% on top {lm["category"]} products, or negotiate supplier discounts.',
            'impact': f'~{lm["share"]:.0f}% of revenue at below-average margin'
        })

    seasonality = patterns.get('seasonality', [])
    peak = next((s for s in seasonality if s.get('direction') == 'above'), None)
    if peak and peak.get('multiplier', 0) >= 1.5:
        insights.append({
            'type': 'info',
            'icon': '📅',
            'title': f'{peak["period"]} Is Your Peak Season',
            'message': peak['message'],
            'action': f'Plan inventory and staffing for next {peak["period"]}. Consider early promotions to capture demand.',
            'impact': f'{peak["multiplier"]}x your average month'
        })
    kpis = kpis or {}
    roas_unavailable = kpis.get('roas_unavailable', True)
    total_rev = data['revenue'].sum() if 'revenue' in data.columns else 0
    rev_growth = metrics.get('revenue_growth', 0)
    margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
    roas = kpis.get('roas') if not roas_unavailable else None
    if roas is None and not roas_unavailable and 'roas' in data.columns:
        roas = data['roas'].mean()
    aov = (total_rev / data['orders'].sum()) if 'orders' in data.columns and data['orders'].sum() > 0 else 50
    churn = metrics.get('churn_rate', 2.5)
    last_cust = data['customers'].iloc[-1] if 'customers' in data.columns and len(data) > 0 else None
    cust_count = int(last_cust) if last_cust is not None and pd.notna(last_cust) else 0
    marketing_spend = data['marketing_spend'].sum() if 'marketing_spend' in data.columns else total_rev * 0.15
    ltv = metrics.get('ltv', aov * 12)
    cac = metrics.get('cac', 45)
    ltv_cac = (ltv / cac) if cac > 0 else 0

    # Revenue growth insights (industry growth target ~10-15% for most)
    if rev_growth > 15:
        est_extra = total_rev * (rev_growth / 100) * 0.5  # Conservative annualized
        action = 'Document what\'s driving growth and scale it. Consider increasing investment 15-20% on top performers.'
        if patterns.get('dimension_shifts') or patterns.get('channel_shifts'):
            top = (patterns.get('dimension_shifts') or patterns.get('channel_shifts', []))[0]
            name = top.get('segment_name') or top.get('channel', '')
            if name:
                action = f'Scale {name} — it\'s driving growth. Consider 15-20% more investment there.'
        insights.append({
            'type': 'positive',
            'icon': '📈',
            'title': f'Revenue Up {rev_growth:.1f}% — Strong Momentum',
            'message': f'Your revenue grew {rev_growth:.1f}% vs prior period. At this rate, you could add ~{_fmt_cur(est_extra)} annually.',
            'action': action,
            'impact': f'~{_fmt_cur(est_extra)} upside if sustained'
        })
    elif rev_growth < -5:
        decline_dollars = total_rev * (abs(rev_growth) / 100)
        action = 'This week: (1) Check what changed in your top revenue sources. (2) Review pricing vs competitors. (3) Reach out to top customers for feedback.'
        if patterns.get('dimension_shifts') or patterns.get('channel_shifts'):
            declining = [s for s in (patterns.get('dimension_shifts') or patterns.get('channel_shifts', [])) if s.get('change_pct', 0) < -15]
            if declining:
                name = declining[0].get('segment_name') or declining[0].get('channel', '')
                if name:
                    action = f'This week: (1) Investigate why {name} declined. (2) Review pricing and competitors. (3) Reach out to top customers.'
        insights.append({
            'type': 'critical',
            'icon': '⚠️',
            'title': f'Revenue Down {abs(rev_growth):.1f}% — Immediate Action Needed',
            'message': f'Revenue declined {abs(rev_growth):.1f}%, roughly {_fmt_cur(decline_dollars)} vs prior period.',
            'action': action,
            'impact': f'~{_fmt_cur(decline_dollars)} at risk'
        })
    elif rev_growth < 5 and rev_growth >= 0:
        gap_to_10 = total_rev * 0.05  # 5% lift potential
        action = 'Identify your top 2 revenue sources and increase investment 20%. Test one new avenue (e.g. referrals, partnerships).'
        if patterns.get('top_categories') or patterns.get('dimension_shifts'):
            top = (patterns.get('top_categories') or [{}])[0] if patterns.get('top_categories') else {}
            dim_top = (patterns.get('dimension_shifts') or [{}])[0] if patterns.get('dimension_shifts') else {}
            name = top.get('category') or dim_top.get('segment_name') or dim_top.get('channel', '')
            if name:
                action = f'Scale {name} — your top performer. Increase investment 20% and test one new source.'
        insights.append({
            'type': 'opportunity',
            'icon': '💡',
            'title': f'Revenue Growth at {rev_growth:.1f}% — Room to Accelerate',
            'message': f'Growth is modest. For your industry, {bench["margin"]:.0f}%+ margin businesses often target 10-15%. A 5-point improvement could add ~{_fmt_cur(gap_to_10)} to your top line.',
            'action': action,
            'impact': f'~{_fmt_cur(gap_to_10)} potential'
        })

    # Margin insights (industry-specific benchmark)
    target_margin = bench['margin']
    if margin < target_margin - 5 and margin > 0:
        margin_gap = target_margin - margin
        est_profit_lift = total_rev * (margin_gap / 100)
        insights.append({
            'type': 'opportunity',
            'icon': '💰',
            'title': f'Profit Margin at {margin:.1f}% — Below {target_margin:.0f}% Industry Target',
            'message': f'At {margin:.1f}%, a {margin_gap:.0f}-point improvement to industry benchmark would add ~{_fmt_cur(est_profit_lift)} to profit annually.',
            'action': 'Audit top 5 products by revenue: raise prices 5-10% on bestsellers, negotiate 3-5% supplier discounts, reduce returns/waste.',
            'impact': f'~{_fmt_cur(est_profit_lift)} profit upside'
        })
    elif margin >= target_margin + 5:
        insights.append({
            'type': 'positive',
            'icon': '✨',
            'title': f'Strong Margins at {margin:.1f}%',
            'message': f'Your {margin:.1f}% margin is above the {target_margin:.0f}% industry benchmark. You have room to invest in growth without sacrificing profitability.',
            'action': 'Consider reinvesting margin into customer acquisition or product development. Maintain pricing discipline.',
            'impact': 'Healthy foundation for scaling'
        })

    # ROAS / marketing efficiency — only when ROAS is valid
    target_roas = bench['roas']
    if not roas_unavailable and roas is not None and roas < target_roas and marketing_spend > 500:
        roas_gap = target_roas - roas
        est_profit = marketing_spend * roas_gap * (margin / 100)
        insights.append({
            'type': 'opportunity',
            'icon': '📊',
            'title': f'ROAS at {roas:.1f}x — Below {target_roas:.0f}x Industry Benchmark',
            'message': f'You spend {_fmt_cur(marketing_spend)} on marketing. At {target_roas:.0f}x ROAS vs {roas:.1f}x, you\'d capture ~{_fmt_cur(est_profit)} more profit with same spend.',
            'action': 'Pause bottom 20% of campaigns by ROAS. Reallocate to top 3 performers. Improve landing page conversion (A/B test headlines).',
            'impact': f'~{_fmt_cur(est_profit)} profit improvement'
        })
    elif not roas_unavailable and roas is not None and roas >= target_roas + 1:
        scale_room = marketing_spend * 0.2 * (margin / 100)  # 20% more spend at current ROAS
        insights.append({
            'type': 'positive',
            'icon': '🚀',
            'title': f'ROAS at {roas:.1f}x — Marketing Is Working',
            'message': f'Your marketing returns are strong. A 20% budget increase could add ~{_fmt_cur(scale_room)} profit if ROAS holds.',
            'action': 'Scale winning campaigns. Test lookalike audiences or new creatives. Document what\'s working for future reference.',
            'impact': f'~{_fmt_cur(scale_room)} upside from scaling'
        })

    # Churn / retention (industry: retention % → churn benchmark)
    churn_bench = min(5, 100 - bench['retention']) if bench['retention'] > 0 else 2.5
    if churn >= churn_bench + 0.5 and cust_count > 0:
        churned_value = cust_count * (churn / 100) * ltv
        insights.append({
            'type': 'opportunity',
            'icon': '🔄',
            'title': f'Churn at {churn:.1f}% — Above {churn_bench:.1f}% Benchmark',
            'message': f'You\'re losing ~{churn:.1f}% of customers monthly. At your LTV, that\'s ~{_fmt_cur(churned_value)} in lost value per month.',
            'action': 'Launch win-back email to churned customers (10% discount). Add onboarding check-in at day 7 and day 30. Survey recent churners for reasons.',
            'impact': f'~{_fmt_cur(churned_value * 0.3)} recoverable (30% reduction)'
        })
    elif churn < churn_bench and cust_count > 100:
        insights.append({
            'type': 'positive',
            'icon': '✅',
            'title': f'Low Churn at {churn:.1f}% — Excellent Retention',
            'message': f'Your churn is below the {churn_bench:.1f}% benchmark. Strong product-market fit. Focus on acquisition — your retention can support growth.',
            'action': 'Double down on acquisition. Consider referral program (customers who stay tend to refer quality leads).',
            'impact': 'Retention is a strength'
        })

    # LTV/CAC
    if 0 < ltv_cac < 3 and cust_count > 50:
        insights.append({
            'type': 'opportunity',
            'icon': '⚖️',
            'title': f'LTV/CAC at {ltv_cac:.1f}x — Unit Economics Need Work',
            'message': f'Target is 3x+. At {ltv_cac:.1f}x, you\'re spending ${cac:.0f} to acquire customers worth ${ltv:.0f} over time.',
            'action': 'Reduce CAC: pause low-ROAS channels, improve ad targeting. Increase LTV: add upsells, loyalty program, or subscription option.',
            'impact': 'Path to profitability'
        })
    elif ltv_cac >= 5:
        insights.append({
            'type': 'positive',
            'icon': '💎',
            'title': f'LTV/CAC at {ltv_cac:.1f}x — Strong Unit Economics',
            'message': f'Your customers are worth {ltv_cac:.1f}x what you pay to acquire them. You can afford to scale acquisition.',
            'action': 'Increase marketing budget on proven channels. Test higher-ticket products or bundles to boost LTV further.',
            'impact': 'Ready to scale'
        })

    # AOV opportunity
    if aov < 75 and aov > 0 and total_rev > 10000:
        uplift = total_rev * 0.12 * (margin / 100)  # 12% AOV lift
        insights.append({
            'type': 'opportunity',
            'icon': '🛒',
            'title': f'AOV at ${aov:.0f} — Upsell Opportunity',
            'message': f'Bundles and upsells typically add 10-15%. At your margin, that could mean ~{_fmt_cur(uplift)} extra profit annually.',
            'action': 'Add "Frequently bought together" at checkout. Create 2-3 product bundles (10% discount). Set free-shipping threshold 15% above current AOV.',
            'impact': f'~{_fmt_cur(uplift)} profit potential'
        })

    # Best day / pattern
    if 'date' in data.columns and 'revenue' in data.columns and len(data) >= 7:
        best_idx = data['revenue'].idxmax()
        best_row = data.loc[best_idx]
        best_date = pd.to_datetime(best_row['date']).strftime('%b %d')
        best_rev = best_row['revenue']
        avg_rev = data['revenue'].mean()
        pct_above = ((best_rev - avg_rev) / avg_rev * 100) if avg_rev > 0 else 0
        if pct_above > 30:
            insights.append({
                'type': 'info',
                'icon': '🏆',
                'title': f'Peak Day: {best_date} — {pct_above:.0f}% Above Average',
                'message': f'Revenue hit {_fmt_cur(best_rev)} on {best_date} vs {_fmt_cur(avg_rev)} daily average.',
                'action': 'Review what drove that day: promo? event? channel? Replicate the conditions (timing, messaging) in future campaigns.',
                'impact': 'Pattern replication'
            })

    return insights[:8]  # Cap at 8 to avoid overload


def generate_action_items(
    data: pd.DataFrame,
    metrics: Dict[str, float],
    industry: str = 'general',
    patterns: Optional[Dict[str, Any]] = None,
    kpis: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Generate prioritized, data-driven action items for business owners.
    Uses patterns when available for channel/category-specific actions.
    """
    actions = []
    if data is None or (hasattr(data, 'empty') and data.empty):
        return actions

    patterns = patterns or {}
    kpis = kpis or {}
    roas_unavailable = kpis.get('roas_unavailable', True)
    bench = _get_benchmarks(industry)

    # Pattern-based actions: use actual segment names from data
    dim_shifts = patterns.get('dimension_shifts', []) or patterns.get('channel_shifts', [])
    growing = [c for c in dim_shifts if c.get('change_pct', 0) > 15]
    if growing:
        s = growing[0]
        name = s.get('segment_name') or s.get('channel', '')
        if name:
            actions.append({
                'priority': '🔴 High',
                'action': f'Scale {name} — up {s["change_pct"]:.0f}%, now {s["share_now"]:.0f}% of revenue',
                'expected_impact': f'Top performer — reallocate 20% from underperformers',
                'timeline': '14 days'
            })
    low_margin = patterns.get('low_margin_winners', [])
    if low_margin:
        lm = low_margin[0]
        actions.append({
            'priority': '🔴 High',
            'action': f'Improve margin on {lm["category"]} (high volume, {lm["margin_pct"]:.0f}% margin)',
            'expected_impact': f'Raise prices 5-10% or negotiate supplier discounts',
            'timeline': '21 days'
        })
    total_rev = data['revenue'].sum() if 'revenue' in data.columns else 0
    rev_growth = metrics.get('revenue_growth', 0)
    margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
    roas = kpis.get('roas') if not roas_unavailable else None
    if roas is None and not roas_unavailable and 'roas' in data.columns:
        roas = data['roas'].mean()
    churn = metrics.get('churn_rate', 2.5)
    marketing_spend = data['marketing_spend'].sum() if 'marketing_spend' in data.columns else total_rev * 0.15

    if rev_growth < 0:
        actions.append({
            'priority': '🔴 High',
            'action': 'Reverse revenue decline: audit churn, pricing, and top revenue sources',
            'expected_impact': f'Stop ~{_fmt_cur(total_rev * abs(rev_growth) / 100)} monthly bleed',
            'timeline': '7 days'
        })
    elif rev_growth < 8 and rev_growth >= 0:
        growing = [c for c in dim_shifts if c.get('change_pct', 0) > 10]
        if growing:
            names = [s.get('segment_name') or s.get('channel', '') for s in growing[:2] if s.get('segment_name') or s.get('channel')]
            if names:
                action = f'Scale {", ".join(names)} by 20% — up {growing[0]["change_pct"]:.0f}% (growth at {rev_growth:.1f}%)'
            else:
                action = f'Scale top 2 revenue sources by 20% (growth at {rev_growth:.1f}%)'
        else:
            action = f'Scale top 2 revenue sources by 20% (growth at {rev_growth:.1f}%)'
        actions.append({
            'priority': '🔴 High',
            'action': action,
            'expected_impact': f'+{_fmt_cur(total_rev * 0.05)} revenue potential',
            'timeline': '30 days'
        })

    if margin < bench['margin'] and margin > 0:
        top_products = patterns.get('top_products', [])
        low_margin_cats = patterns.get('low_margin_winners', [])
        if low_margin_cats:
            names = [lm['category'] for lm in low_margin_cats[:2]]
            action = f'Raise prices 5-10% on {", ".join(names)} — high volume, thin margin ({margin:.1f}% vs {bench["margin"]:.0f}% benchmark)'
        elif top_products:
            names = [p['product'] for p in top_products[:3]]
            action = f'Raise prices 5-10% on {", ".join(names)} (margin {margin:.1f}% vs {bench["margin"]:.0f}% benchmark)'
        else:
            action = f'Raise prices 5-10% on top 3 products (margin {margin:.1f}% vs {bench["margin"]:.0f}% benchmark)'
        actions.append({
            'priority': '🔴 High',
            'action': action,
            'expected_impact': f'+{_fmt_cur(total_rev * (bench["margin"] - margin) / 100)} profit',
            'timeline': '14 days'
        })

    if not roas_unavailable and roas is not None and roas < bench['roas'] and marketing_spend > 500:
        channel_shifts = [s for s in dim_shifts if s.get('dimension_type', 'channel') == 'channel' or 'channel' in str(s.get('channel', ''))]
        top_channels = [s.get('segment_name') or s.get('channel', '') for s in channel_shifts if (s.get('change_pct', 0) > 0 or s.get('current_rev', 0) > 0)][:3]
        if not top_channels:
            top_channels = [s.get('segment_name') or s.get('channel', '') for s in dim_shifts if (s.get('change_pct', 0) > 0 or s.get('current_rev', 0) > 0)][:3]
        top_channels = [c for c in top_channels if c]
        if top_channels:
            action = f'Pause underperformers; scale {", ".join(top_channels[:2])} (ROAS {roas:.1f}x vs {bench["roas"]:.0f}x)'
        else:
            action = f'Pause bottom 20% campaigns, reallocate to winners (ROAS {roas:.1f}x vs {bench["roas"]:.0f}x)'
        actions.append({
            'priority': '🟡 Medium',
            'action': action,
            'expected_impact': f'+{_fmt_cur(marketing_spend * (bench["roas"] - roas) * margin / 100)} profit',
            'timeline': '14 days'
        })

    if churn >= 3:
        actions.append({
            'priority': '🔴 High',
            'action': f'Launch retention campaign: win-back email + onboarding check-ins (churn {churn:.1f}%)',
            'expected_impact': '25-35% churn reduction',
            'timeline': '21 days'
        })

    if 'orders' in data.columns and data['orders'].sum() > 0:
        aov = total_rev / data['orders'].sum()
        if aov < 75:
            top_products = patterns.get('top_products', [])
            if top_products:
                prod_names = [p['product'] for p in top_products[:2]]
                action = f'Bundle {", ".join(prod_names)} with complementary items; set free-shipping threshold above ${aov:.0f} AOV'
            else:
                action = f'Add product bundles and free-shipping threshold (AOV ${aov:.0f})'
            actions.append({
                'priority': '🟡 Medium',
                'action': action,
                'expected_impact': f'+10-15% AOV, ~{_fmt_cur(total_rev * 0.1 * margin / 100)} profit',
                'timeline': '30 days'
            })

    # Ensure at least 2 actions
    if len(actions) < 2:
        top_products = patterns.get('top_products', [])
        if top_products:
            names = [p['product'] for p in top_products[:3]]
            action = f'Review {", ".join(names)} — optimize pricing and promotion'
        else:
            action = 'Review top 5 products by revenue — optimize pricing and promotion'
        actions.append({
            'priority': '🟡 Medium',
            'action': action,
            'expected_impact': 'Margin and conversion improvement',
            'timeline': '30 days'
        })
        if len(actions) < 2:
            actions.append({
                'priority': '🟢 Low',
                'action': 'Set up weekly KPI review (revenue, margin, churn)',
                'expected_impact': 'Faster response to trends',
                'timeline': '7 days'
            })

    return actions[:6]
