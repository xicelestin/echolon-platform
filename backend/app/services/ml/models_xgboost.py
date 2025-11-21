"""XGBoost model training and prediction for time-series forecasting."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy.orm import Session

from .preprocessing import prepare_data_for_xgboost, load_timeseries_data, clean_timeseries_data
from .preprocessing import add_date_features, add_lag_features, add_rolling_features
from .config import XGBOOST_CONFIG, MODELS_STORE_DIR, TRAIN_TEST_SPLIT
from .schemas import ForecastPoint


def train_xgboost_model(
    session: Session,
    business_id: int,
    metric_name: str,
    horizon: int = 30
) -> Tuple[str, dict]:
    """
    Train XGBoost model on historical data.
    
    Args:
        session: Database session
        business_id: Business ID
        metric_name: Metric name to forecast
        horizon: Forecast horizon (not used in training but saved with model)
    
    Returns:
        Tuple of (model_path, metrics_dict)
    """
    # Load and prepare data
    X, y = prepare_data_for_xgboost(session, business_id, metric_name)
    
    # Split data
    split_idx = int(len(X) * TRAIN_TEST_SPLIT)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train model
    model = xgb.XGBRegressor(**XGBOOST_CONFIG)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    metrics = {
        "mae": float(mae),
        "rmse": float(rmse),
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }
    
    # Save model
    model_path = MODELS_STORE_DIR / f"xgboost_{business_id}_{metric_name}.json"
    model.save_model(str(model_path))
    
    return str(model_path), metrics


def predict_xgboost(
    session: Session,
    business_id: int,
    metric_name: str,
    horizon: int = 30
) -> List[ForecastPoint]:
    """
    Generate forecasts using trained XGBoost model.
    
    Args:
        session: Database session
        business_id: Business ID  
        metric_name: Metric name to forecast
        horizon: Number of days to forecast
    
    Returns:
        List of ForecastPoint objects
    """
    # Load model
    model_path = MODELS_STORE_DIR / f"xgboost_{business_id}_{metric_name}.json"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. Train model first."
        )
    
    model = xgb.XGBRegressor()
    model.load_model(str(model_path))
    
    # Load historical data
    df = load_timeseries_data(session, business_id, metric_name)
    df = clean_timeseries_data(df)
    
    # Add features
    df = add_date_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = df.dropna()
    
    # Get last date and latest feature values
    last_date = df['date'].max()
    latest_values = df['value'].values
    
    # Generate predictions
    predictions = []
    current_date = last_date
    
    for i in range(horizon):
        current_date = current_date + timedelta(days=1)
        
        # Create features for prediction
        features = {}
        features['day_of_week'] = current_date.dayofweek
        features['day_of_month'] = current_date.day
        features['month'] = current_date.month
        features['quarter'] = (current_date.month - 1) // 3 + 1
        features['year'] = current_date.year
        features['is_weekend'] = 1 if current_date.dayofweek >= 5 else 0
        features['is_month_start'] = 1 if current_date.day == 1 else 0
        features['is_month_end'] = 1 if current_date.day == current_date.replace(
            day=1, month=current_date.month % 12 + 1).day else 0
        
        # Lag features (use most recent predictions)
        lag_values = list(latest_values[-30:]) + [p.value for p in predictions]
        for lag in [1, 7, 14, 30]:
            if len(lag_values) >= lag:
                features[f'lag_{lag}'] = lag_values[-lag]
            else:
                features[f'lag_{lag}'] = latest_values[-1]
        
        # Rolling features
        for window in [7, 14, 30]:
            recent_vals = lag_values[-window:] if len(lag_values) >= window else lag_values
            features[f'rolling_mean_{window}'] = np.mean(recent_vals)
            features[f'rolling_std_{window}'] = np.std(recent_vals)
        
        # Create feature vector in correct order
        feature_names = model.get_booster().feature_names
        X_pred = pd.DataFrame([features])[feature_names]
        
        # Predict
        pred_value = model.predict(X_pred)[0]
        
        predictions.append(
            ForecastPoint(
                date=current_date.date(),
                value=float(pred_value),
                lower_bound=None,  # XGBoost doesn't provide confidence intervals by default
                upper_bound=None
            )
        )
    
    return predictions


def model_exists(business_id: int, metric_name: str) -> bool:
    """
    Check if a trained model exists.
    
    Args:
        business_id: Business ID
        metric_name: Metric name
    
    Returns:
        True if model file exists
    """
    model_path = MODELS_STORE_DIR / f"xgboost_{business_id}_{metric_name}.json"
    return model_path.exists()
