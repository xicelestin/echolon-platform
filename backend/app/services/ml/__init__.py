"""ML package for forecasting and analytics in Echolon AI.

This package provides machine learning capabilities including:
- XGBoost-based forecasting
- Prophet baseline models
- Time-series preprocessing and feature engineering
- AI-powered insights generation
"""

# Optional imports - fail gracefully if dependencies not available
try:
    from .forecast_service import ForecastService
    from .insights_service import InsightsService
    from .schemas import ForecastRequest, ForecastResponse, ForecastPoint
    
    __all__ = [
        "ForecastService",
        "InsightsService",
        "ForecastRequest",
        "ForecastResponse",
        "ForecastPoint",
    ]
except ImportError as e:
    print(f"ML services not fully available: {e}")
    __all__ = []
