"""Data-driven recommendations engine - generates personalized insights from actual metrics."""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from utils import calculate_key_metrics


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
    Returns list of recommendation dicts with title, impact, why, steps, confidence, category.
    """
    metrics = compute_business_metrics(data)
    recs = []
    
    total_revenue = metrics.get('total_revenue', 0)
    rev_growth = metrics.get('revenue_growth', 0)
    margin = metrics.get('avg_profit_margin', 40)
    roas = metrics.get('roas', 3)
    aov = metrics.get('avg_order_value', 50)
    cust_count = metrics.get('total_customers', 1000)
    churn = metrics.get('churn_rate', 5)
    marketing_spend = metrics.get('marketing_spend', total_revenue * 0.15)
    
    # Revenue recommendations
    if rev_growth < 15 and rev_growth >= 0:
        est_impact = total_revenue * 0.08  # 8% uplift potential
        recs.append({
            'category': 'revenue',
            'title': 'Scale Marketing on Top Channels',
            'impact': f'+{format_currency_short(est_impact)} annually (est. 8-12% revenue lift)',
            'why': f'Your revenue growth is {rev_growth:.1f}%. Industry leaders achieve 15%+. Your ROAS of {roas:.1f}x suggests room to scale winning campaigns.',
            'steps': [
                'Identify top 3 channels by ROAS',
                'Increase budget 20% on winners',
                'Pause or reduce underperformers',
                'Monitor conversion rates weekly'
            ],
            'confidence': min(85, 70 + int(roas)),
            'cost_benefit': 'Low cost | High upside'
        })
    
    if margin < 35 and margin > 0:
        margin_gap = 35 - margin
        est_impact = total_revenue * (margin_gap / 100)
        recs.append({
            'category': 'revenue',
            'title': 'Improve Profit Margins',
            'impact': f'+{format_currency_short(est_impact)} annually (moving to 35% margin)',
            'why': f'At {margin:.1f}% margin, a 5-point improvement captures significant value. Top quartile businesses achieve 40%+.',
            'steps': [
                'Audit product-level margins',
                'Raise prices on bestsellers 5-10%',
                'Negotiate supplier discounts',
                'Reduce fulfillment waste'
            ],
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
        recs.append({
            'category': 'efficiency',
            'title': 'Optimize Marketing ROI',
            'impact': f'+{format_currency_short(est_impact)} profit (ROAS 4x vs current {roas:.1f}x)',
            'why': f'Your ROAS of {roas:.1f}x is below 4x benchmark. Reallocating from underperformers to winners typically yields 30-50% efficiency gain.',
            'steps': [
                'Audit all campaigns by ROAS',
                'Pause bottom 20% performers',
                'Increase top 3 channels 25%',
                'Improve landing page conversion'
            ],
            'confidence': 85,
            'cost_benefit': 'Zero additional spend | Better returns'
        })
    
    if aov < 75 and aov > 0:
        uplift = 0.15  # 15% AOV increase potential
        est_impact = total_revenue * uplift * margin / 100
        recs.append({
            'category': 'efficiency',
            'title': 'Increase Average Order Value',
            'impact': f'+{format_currency_short(est_impact)} profit (15% AOV uplift)',
            'why': f'Your AOV is ${aov:.0f}. Upsells and bundles typically add 10-20%. Low effort, high margin impact.',
            'steps': [
                'Add "Frequently bought together" section',
                'Create product bundles (10-15% discount)',
                'Implement minimum for free shipping',
                'Train staff on add-on suggestions'
            ],
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
