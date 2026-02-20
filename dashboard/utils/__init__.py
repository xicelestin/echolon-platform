# -*- coding: utf-8 -*-
"""
Echolon AI Dashboard - Utilities Package

Provides utility functions and classes for the dashboard.
"""

# from .data_validation import (
    #     DataValidator,
    #     validate_dashboard_data,
    #     get_validated_data,
    #     safe_divide
# )

from .export_utils import (
    create_download_button,
    create_multi_format_export,
    create_filtered_export_section,
    export_with_metadata,
    to_csv,
    to_excel,
    to_json
)
from .metrics_utils import (
    calculate_period_comparison,
    get_period_data,
    calculate_business_health_score,
    calculate_key_metrics,
    calculate_ltv,
    get_goal_progress,
    format_currency,
    format_percentage,
    get_trend_indicator
)
from .driver_analysis import get_change_explanation, analyze_revenue_drivers
from .data_patterns import analyze_data_patterns
from .alerts import get_metric_alerts
from .personalized_insights import (
    generate_personalized_insights,
    generate_action_items,
    get_top_priority_this_week,
    get_what_changed,
    get_quick_wins,
    get_progress_callouts,
)

__all__ = [
#         'DataValidator',
    #     'validate_dashboard_data',
    #     'get_validated_data',
    #     'safe_divide'
        # Export utilities
    'create_download_button',
    'create_multi_format_export',
    'create_filtered_export_section',
    'export_with_metadata',
    'to_csv',
    'to_excel',
    'to_json',    # Metrics utilities
    'calculate_period_comparison',
    'get_period_data',
    'calculate_business_health_score',
    'calculate_key_metrics',
    'calculate_ltv',
    'get_goal_progress',
    'format_currency',
    'format_percentage',
    'get_trend_indicator',
    'generate_personalized_insights',
    'generate_action_items',
    'get_top_priority_this_week',
    'get_what_changed',
    'get_quick_wins',
    'get_progress_callouts',
    'get_change_explanation',
    'analyze_revenue_drivers',
    'analyze_data_patterns',
    'get_metric_alerts',
]

__version__ = '1.0.0'
