"""Prophet model training and prediction for time-series forecasting."""

import pandas as pd
import pickle
from datetime import datetime
from typing import List, Tuple
from pathlib import Path
from prophet import Prophet
from sqlalchemy.orm import Session

from .preprocessing import prepare_data_for_prophet
from .config import PROPHET_CONFIG, MODELS_STORE_DIR
from .schemas import ForecastPoint


def train_prophet_model(
    session: Session,
    business_id: int,
    metric_name: str,
    horizon: int = 30
) -> Tuple[str, dict]:
    """
    Train Prophet model on historical data.
    
    Args:
        session: Database session
        business_id: Business ID
        metric_name: Metric name to forecast
        horizon: Forecast horizon (not used in training)
    
    Returns:
        Tuple of (model_path, metrics_dict)
    """
    # Load and prepare data
    df = prepare_data_for_prophet(session, business_id, metric_name)
    
    # Initialize and train Prophet model
    model = Prophet(**PROPHET_CONFIG)
    model.fit(df)
    
    # Generate in-sample predictions for evaluation
    forecast = model.predict(df)
    
    # Calculate metrics
    y_true = df['y'].values
    y_pred = forecast['yhat'].values[:len(y_true)]
    mae = abs(y_true - y_pred).mean()
    rmse = ((y_true - y_pred) ** 2).mean() ** 0.5
    
    metrics = {
        "mae": float(mae),
        "rmse": float(rmse),
        "train_samples": len(df)
    }
    
    # Save model using pickle
    model_path = MODELS_STORE_DIR / f"prophet_{business_id}_{metric_name}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    return str(model_path), metrics


def predict_prophet(
    session: Session,
    business_id: int,
    metric_name: str,
    horizon: int = 30
) -> List[ForecastPoint]:
    """
    Generate forecasts using trained Prophet model.
    
    Args:
        session: Database session
        business_id: Business ID
        metric_name: Metric name to forecast
        horizon: Number of days to forecast
    
    Returns:
        List of ForecastPoint objects with confidence intervals
    """
    # Load model
    model_path = MODELS_STORE_DIR / f"prophet_{business_id}_{metric_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. Train model first."
        )
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=horizon)
    
    # Make predictions
    forecast = model.predict(future)
    
    # Extract future predictions (last 'horizon' rows)
    future_forecast = forecast.tail(horizon)
    
    # Convert to ForecastPoint objects
    predictions = []
    for _, row in future_forecast.iterrows():
        predictions.append(
            ForecastPoint(
                date=row['ds'].date(),
                value=float(row['yhat']),
                lower_bound=float(row['yhat_lower']),
                upper_bound=float(row['yhat_upper'])
            )
        )
    
    return predictions


def model_exists(business_id: int, metric_name: str) -> bool:
    """
    Check if a trained Prophet model exists.
    
    Args:
        business_id: Business ID
        metric_name: Metric name
    
    Returns:
        True if model file exists
    """
    model_path = MODELS_STORE_DIR / f"prophet_{business_id}_{metric_name}.pkl"
    return model_path.exists()
