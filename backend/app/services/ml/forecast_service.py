"""Forecast service orchestrating ML model training and predictions."""

from typing import Optional
from sqlalchemy.orm import Session

from .schemas import ForecastRequest, ForecastResponse

# Optional model imports - catch any error (ImportError, XGBoostError, etc.)
try:
    from .models_xgboost import train_xgboost_model, predict_xgboost, model_exists as xgboost_exists
    HAS_XGBOOST = True
except Exception as e:
    HAS_XGBOOST = False
    print(f"XGBoost not available: {e}")
    def xgboost_exists(*args, **kwargs): return False
    def train_xgboost_model(*args, **kwargs): raise ImportError("XGBoost not available")
    def predict_xgboost(*args, **kwargs): raise ImportError("XGBoost not available")

try:
    from .models_prophet import train_prophet_model, predict_prophet, model_exists as prophet_exists
    HAS_PROPHET = True
except Exception as e:
    HAS_PROPHET = False
    print(f"Prophet not available: {e}")
    def prophet_exists(*args, **kwargs): return False
    def train_prophet_model(*args, **kwargs): raise ImportError("Prophet not available")
    def predict_prophet(*args, **kwargs): raise ImportError("Prophet not available")


class ForecastService:
    """Service for generating time-series forecasts."""
    
    @staticmethod
    def generate_forecast(
        session: Session,
        request: ForecastRequest
    ) -> ForecastResponse:
        """
        Generate forecast using specified or best available model.
        
        Args:
            session: Database session
            request: ForecastRequest with business_id, metric_name, horizon, model_type
        
        Returns:
            ForecastResponse with predictions
        """
        business_id = request.business_id
        metric_name = request.metric_name
        horizon = request.horizon
        model_type = request.model_type
        
        # Determine which model to use
        if model_type == "auto":
            # Check which models exist, prefer XGBoost
            if HAS_XGBOOST and xgboost_exists(business_id, metric_name):
                chosen_model = "xgboost"
            elif HAS_PROPHET and prophet_exists(business_id, metric_name):
                chosen_model = "prophet"
            elif HAS_XGBOOST:
                # No model exists, train XGBoost by default if available
                chosen_model = "xgboost"
            elif HAS_PROPHET:
                chosen_model = "prophet"
            else:
                raise ValueError("No ML models available. Please install XGBoost or Prophet.")
        else:
            chosen_model = model_type
            if chosen_model == "xgboost" and not HAS_XGBOOST:
                raise ValueError("XGBoost not available. Please install: pip install xgboost")
            if chosen_model == "prophet" and not HAS_PROPHET:
                raise ValueError("Prophet not available. Please install: pip install prophet")
        
        # Train model if it doesn't exist
        if chosen_model == "xgboost":
            if not xgboost_exists(business_id, metric_name):
                print(f"Training XGBoost model for business {business_id}, metric {metric_name}...")
                _, metrics = train_xgboost_model(session, business_id, metric_name, horizon)
                print(f"XGBoost training complete. Metrics: {metrics}")
            
            # Generate predictions
            forecast_points = predict_xgboost(session, business_id, metric_name, horizon)
            
        elif chosen_model == "prophet":
            if not prophet_exists(business_id, metric_name):
                print(f"Training Prophet model for business {business_id}, metric {metric_name}...")
                _, metrics = train_prophet_model(session, business_id, metric_name, horizon)
                print(f"Prophet training complete. Metrics: {metrics}")
            
            # Generate predictions
            forecast_points = predict_prophet(session, business_id, metric_name, horizon)
        
        else:
            raise ValueError(f"Unknown model type: {chosen_model}. Use 'xgboost', 'prophet', or 'auto'.")
        
        # Return response
        return ForecastResponse(
            business_id=business_id,
            metric_name=metric_name,
            horizon=horizon,
            model_used=chosen_model,
            points=forecast_points,
            metrics=None  # Can optionally add model metrics here
        )
    
    @staticmethod
    def train_model(
        session: Session,
        business_id: int,
        metric_name: str,
        model_type: str = "xgboost",
        horizon: int = 30
    ) -> dict:
        """
        Explicitly train a specific model.
        
        Args:
            session: Database session
            business_id: Business ID
            metric_name: Metric name
            model_type: 'xgboost' or 'prophet'
            horizon: Forecast horizon
        
        Returns:
            dict with model_path and metrics
        """
        if model_type == "xgboost":
            model_path, metrics = train_xgboost_model(session, business_id, metric_name, horizon)
        elif model_type == "prophet":
            model_path, metrics = train_prophet_model(session, business_id, metric_name, horizon)
        else:
            raise ValueError(f"Unknown model type: {model_type}. Use 'xgboost' or 'prophet'.")
        
        return {
            "model_type": model_type,
            "model_path": model_path,
            "metrics": metrics,
            "business_id": business_id,
            "metric_name": metric_name
        }
