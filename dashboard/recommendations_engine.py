"""Data-driven recommendations engine - generates personalized insights from actual metrics."""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from utils import calculate_key_metrics
from utils.data_patterns import analyze_data_patterns


def compute_business_metrics(data: pd.DataFrame) -> Dict[str, float]:
    """Compute all metrics needed for recommendations."""
    metrics = calculate_key_metrics(data)
    
    # Add derived metrics
    if 'revenue' in data.columns:
        metrics['total_revenue'] = data['revenue'].sum()
        metrics['avg_daily_revenue'] = data['revenue'].mean()
    if 'orders' in data.columns and data['orders'].sum() > 0:
        metrics['avg_order_value'] = data['revenue'].sum() / data['orders'].sum()
    if 'profit_margin' in data.columns:
        metrics['avg_profit_margin'] = data['profit_margin'].mean()
    if 'roas' in data.columns:
        metrics['roas'] = data['roas'].mean()
    if 'marketing_spend' in data.columns:
        metrics['marketing_spend'] = data['marketing_spend'].sum()
    if 'customers' in data.columns:
        metrics['total_customers'] = data['customers'].iloc[-1] if len(data) > 0 else 0
    
    return metrics


def generate_data_driven_recommendations(data: pd.DataFrame, industry: str = 'ecommerce') -> List[Dict[str, Any]]:
    """
    Generate personalized recommendations from actual business data.
    Uses patterns (channels, products, categories) when available for specific steps.
    Returns list of recommendation dicts with title, impact, why, steps, confidence, category.
    """
    metrics = compute_business_metrics(data)
    pattern_result = analyze_data_patterns(data)
    patterns = pattern_result.get('patterns', {}) if pattern_result.get('has_data') else {}
    
    recs = []
    
    total_revenue = metrics.get('total_revenue', 0)
    rev_growth = metrics.get('revenue_growth', 0)
    margin = metrics.get('avg_profit_margin', 40)
    roas = metrics.get('roas', 3)
    aov = metrics.get('avg_order_value', 50)
    cust_count = metrics.get('total_customers', 1000)
    churn = metrics.get('churn_rate', 5)
    marketing_spend = metrics.get('marketing_spend', total_revenue * 0.15)
    
    # Segment names from patterns (for personalized steps)
    dim_shifts = patterns.get('dimension_shifts', []) or patterns.get('channel_shifts', [])
    top_channels = [s['segment_name'] for s in dim_shifts if s.get('change_pct', 0) > 0 and s.get('dimension_type', 'channel') == 'channel'][:3]
    if not top_channels:
        top_channels = [s['segment_name'] for s in dim_shifts if s.get('change_pct', 0) > 0][:3]  # fallback to any dimension
    top_products = [p['product'] for p in patterns.get('top_products', [])][:3]
    top_categories = [c['category'] for c in patterns.get('top_categories', [])][:3]
    low_margin = patterns.get('low_margin_winners', [])
    
    # Revenue recommendations
    if rev_growth < 15 and rev_growth >= 0:
        est_impact = total_revenue * 0.08  # 8% uplift potential
        if top_channels:
            steps = [
                f'Scale {top_channels[0]} — your top performer',
                f'Increase budget 20% on {", ".join(top_channels[:2])}',
                'Pause or reduce underperformers',
                'Monitor conversion rates weekly'
            ]
        else:
            steps = [
                'Identify top 3 channels by ROAS',
                'Increase budget 20% on winners',
                'Pause or reduce underperformers',
                'Monitor conversion rates weekly'
            ]
        recs.append({
            'category': 'revenue',
            'title': f'Scale Marketing on Top Channels' + (f' ({top_channels[0]})' if top_channels else ''),
            'impact': f'+{format_currency_short(est_impact)} annually (est. 8-12% revenue lift)',
            'why': f'Your revenue growth is {rev_growth:.1f}%. Industry leaders achieve 15%+. Your ROAS of {roas:.1f}x suggests room to scale winning campaigns.',
            'steps': steps,
            'confidence': min(85, 70 + int(roas)),
            'cost_benefit': 'Low cost | High upside'
        })
    
    if margin < 35 and margin > 0:
        margin_gap = 35 - margin
        est_impact = total_revenue * (margin_gap / 100)
        if low_margin:
            lm_names = [lm['category'] for lm in low_margin[:2]]
            steps = [
                f'Raise prices 5-10% on {lm_names[0]} — high volume, thin margin',
                f'Audit margins on {", ".join(lm_names)}',
                'Negotiate supplier discounts',
                'Reduce fulfillment waste'
            ]
        elif top_products:
            steps = [
                f'Raise prices 5-10% on {top_products[0]} (top seller)',
                f'Audit margins on {", ".join(top_products[:3])}',
                'Negotiate supplier discounts',
                'Reduce fulfillment waste'
            ]
        elif top_categories:
            steps = [
                f'Raise prices on {top_categories[0]} — your largest category',
                f'Audit margins across {", ".join(top_categories[:2])}',
                'Negotiate supplier discounts',
                'Reduce fulfillment waste'
            ]
        else:
            steps = [
                'Audit product-level margins',
                'Raise prices on bestsellers 5-10%',
                'Negotiate supplier discounts',
                'Reduce fulfillment waste'
            ]
        recs.append({
            'category': 'revenue',
            'title': 'Improve Profit Margins' + (f' ({low_margin[0]["category"]})' if low_margin else ''),
            'impact': f'+{format_currency_short(est_impact)} annually (moving to 35% margin)',
            'why': f'At {margin:.1f}% margin, a 5-point improvement captures significant value. Top quartile businesses achieve 40%+.',
            'steps': steps,
            'confidence': 82,
            'cost_benefit': 'Minimal cost | Direct impact'
        })
    
    # Retention recommendations
    if churn > 2 or (churn == 0 and cust_count > 0):
        effective_churn = churn if churn > 0 else 3  # Assume 3% if not calculated
        ltv_estimate = (total_revenue / cust_count) * 12 if cust_count > 0 else 500
        est_savings = cust_count * (effective_churn / 100) * ltv_estimate * 0.3  # 30% reduction
        recs.append({
            'category': 'retention',
            'title': 'Launch Loyalty Program',
            'impact': f'Reduce churn 25-35% (save ~{format_currency_short(est_savings)} in LTV)',
            'why': f'Customers with 4+ purchases churn 5x less. Loyalty programs increase repeat rate 23% (HubSpot). Your LTV opportunity is significant.',
            'steps': [
                'Design tiered rewards (Bronze/Silver/Gold)',
                'Integrate points into checkout',
                'Email launch to existing customers',
                'Track repeat purchase rate weekly'
            ],
            'confidence': 88,
            'cost_benefit': '~$5-10K build | High LTV retention'
        })
    
    # Efficiency recommendations
    if roas < 4 and marketing_spend > 1000:
        roas_gap = 4 - roas
        est_impact = marketing_spend * roas_gap * (margin / 100)
        if top_channels:
            steps = [
                f'Pause underperformers; scale {top_channels[0]}',
                f'Increase budget 25% on {", ".join(top_channels[:2])}',
                'Audit all campaigns by ROAS',
                'Improve landing page conversion'
            ]
        else:
            steps = [
                'Audit all campaigns by ROAS',
                'Pause bottom 20% performers',
                'Increase top 3 channels 25%',
                'Improve landing page conversion'
            ]
        recs.append({
            'category': 'efficiency',
            'title': 'Optimize Marketing ROI' + (f' — scale {top_channels[0]}' if top_channels else ''),
            'impact': f'+{format_currency_short(est_impact)} profit (ROAS 4x vs current {roas:.1f}x)',
            'why': f'Your ROAS of {roas:.1f}x is below 4x benchmark. Reallocating from underperformers to winners typically yields 30-50% efficiency gain.',
            'steps': steps,
            'confidence': 85,
            'cost_benefit': 'Zero additional spend | Better returns'
        })
    
    if aov < 75 and aov > 0:
        uplift = 0.15  # 15% AOV increase potential
        est_impact = total_revenue * uplift * margin / 100
        if top_products:
            steps = [
                f'Bundle {top_products[0]} with complementary items',
                'Add "Frequently bought together" at checkout',
                'Create product bundles (10-15% discount)',
                f'Set free-shipping threshold 15% above ${aov:.0f} AOV'
            ]
        else:
            steps = [
                'Add "Frequently bought together" section',
                'Create product bundles (10-15% discount)',
                'Implement minimum for free shipping',
                'Train staff on add-on suggestions'
            ]
        recs.append({
            'category': 'efficiency',
            'title': 'Increase Average Order Value' + (f' (${aov:.0f} → target $75+)' if aov else ''),
            'impact': f'+{format_currency_short(est_impact)} profit (15% AOV uplift)',
            'why': f'Your AOV is ${aov:.0f}. Upsells and bundles typically add 10-20%. Low effort, high margin impact.',
            'steps': steps,
            'confidence': 80,
            'cost_benefit': 'Low effort | High margin'
        })
    
    # Innovation - only when business is ready (revenue scale + repeat potential)
    if total_revenue > 100000 and cust_count > 200 and churn < 4:
        recs.append({
            'category': 'innovation',
            'title': 'Add Subscription Option',
            'impact': f'+{format_currency_short(total_revenue * 0.12)} recurring revenue (12% of customers)',
            'why': f'At {cust_count} customers and {churn:.1f}% churn, you have repeat buyers. Subscriptions increase LTV 6-8x.',
            'steps': [
                'Design monthly/annual tiers',
                'Build auto-renewal flow',
                'Offer 10% discount for annual',
                'Migrate 20-30% of repeat buyers'
            ],
            'confidence': 78,
            'cost_benefit': '~$15-25K build | 6-12 month payback'
        })
    
    return recs[:6]  # Top 6


def format_currency_short(value: float) -> str:
    """Short currency format for recommendations."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value/1_000:.0f}K"
    return f"${value:.0f}"
