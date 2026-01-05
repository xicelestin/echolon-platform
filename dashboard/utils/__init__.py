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

__all__ = [
    'DataValidator',
    'validate_dashboard_data',
    'get_validated_data',
    'safe_divide'
]

__version__ = '1.0.0'
