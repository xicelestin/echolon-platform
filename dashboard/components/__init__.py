"""
Components Package - Chart and UI utilities for Echolon Dashboard
"""

from .charts import (
    create_line_chart,
    create_bar_chart,
    create_pie_chart,
    create_stacked_area_chart,
    create_scatter_plot,
    create_heatmap,
    create_gauge_chart,
    create_metric_card_chart,
    apply_default_layout,
    COLORS,
    COLOR_PALETTE
)

from .enhanced_metrics import (
    display_business_health_score,
    display_metric_with_comparison,
    display_key_metrics_grid,
    display_unavailable_metric,
    display_metric_with_dollar_impact,
    display_explain_this_number,
)

__all__ = [
    'create_line_chart',
    'create_bar_chart',
    'create_pie_chart',
    'create_stacked_area_chart',
    'create_scatter_plot',
    'create_heatmap',
    'create_gauge_chart',
    'create_metric_card_chart',
    'apply_default_layout',
    'COLORS',
    'COLOR_PALETTE',
    'display_business_health_score',
    'display_metric_with_comparison',
    'display_key_metrics_grid',
    'display_unavailable_metric',
    'display_metric_with_dollar_impact',
    'display_explain_this_number',
]
