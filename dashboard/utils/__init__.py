# -*- coding: utf-8 -*-
"""
Echolon AI Dashboard - Utilities Package

Provides utility functions and classes for the dashboard.
"""

from .data_validation import (
    DataValidator,
    validate_dashboard_data,
    get_validated_data,
    safe_divide
)

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
    get_goal_progress,
    format_currency,
    format_percentage,
    get_trend_indicator
)

__all__ = [
    'DataValidator',
    'validate_dashboard_data',
    'get_validated_data',
    'safe_divide'
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
    'get_goal_progress',
    'format_currency',
    'format_percentage',
    'get_trend_indicator'
]

__version__ = '1.0.0'
