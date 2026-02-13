"""Industry-specific metrics and configurations."""
from typing import Dict, List, Any

INDUSTRIES = {
    'ecommerce': {
        'name': 'E-commerce / Retail',
        'icon': '🛒',
        'key_metrics': ['revenue', 'orders', 'aov', 'conversion_rate', 'inventory_turnover'],
        'benchmarks': {'profit_margin': 35, 'roas': 4, 'retention': 70},
        'description': 'Online retail, D2C brands, marketplaces'
    },
    'saas': {
        'name': 'SaaS / Software',
        'icon': '💻',
        'key_metrics': ['mrr', 'arr', 'churn', 'ltv', 'cac', 'ltv_cac_ratio'],
        'benchmarks': {'profit_margin': 70, 'roas': 5, 'retention': 90},
        'description': 'Subscription software, B2B SaaS'
    },
    'restaurant': {
        'name': 'Restaurant / Food Service',
        'icon': '🍽️',
        'key_metrics': ['revenue', 'covers', 'avg_check', 'food_cost_pct', 'labor_cost_pct'],
        'benchmarks': {'profit_margin': 10, 'roas': 3, 'retention': 50},
        'description': 'Restaurants, cafes, catering'
    },
    'services': {
        'name': 'Professional Services',
        'icon': '📋',
        'key_metrics': ['revenue', 'utilization', 'project_margin', 'billable_hours'],
        'benchmarks': {'profit_margin': 25, 'roas': 4, 'retention': 80},
        'description': 'Consulting, agencies, freelancers'
    },
    'general': {
        'name': 'General Business',
        'icon': '📊',
        'key_metrics': ['revenue', 'profit', 'margin', 'customers', 'roas'],
        'benchmarks': {'profit_margin': 40, 'roas': 4, 'retention': 75},
        'description': 'Mixed or unspecified business type'
    }
}


def get_industry_config(industry_key: str) -> Dict[str, Any]:
    """Get configuration for an industry."""
    return INDUSTRIES.get(industry_key, INDUSTRIES['general'])


def get_industry_metrics_to_show(industry_key: str, available_columns: List[str]) -> List[str]:
    """Return which metrics to emphasize for this industry."""
    config = get_industry_config(industry_key)
    preferred = config.get('key_metrics', [])
    return [m for m in preferred if m in available_columns or m.replace('_', ' ') in str(available_columns)]


def get_industry_benchmarks(industry_key: str) -> Dict[str, float]:
    """Get benchmark values for industry."""
    return get_industry_config(industry_key).get('benchmarks', INDUSTRIES['general']['benchmarks'])
