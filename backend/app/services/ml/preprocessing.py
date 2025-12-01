"""Data preprocessing and feature engineering for time-series forecasting."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.models.models import BusinessData
from .config import LAG_FEATURES, ROLLING_WINDOWS, MIN_TRAINING_SAMPLES


def load_timeseries_data(
    session: Session,
    business_id: int,
    metric_name: str
) -> pd.DataFrame:
    """
    Load time-series data from BusinessData table.
    
    Args:
        session: SQLAlchemy database session
        business_id: ID of the business
        metric_name: Name of the metric to load
    
    Returns:
        DataFrame with 'date' and 'value' columns
    """
    # Query BusinessData filtered by business_id
    query = session.query(BusinessData).filter(
        BusinessData.user_id == business_id
    ).all()
    
    # Extract time-series from JSON data
    records = []
    for record in query:
        if record.data:
            # Handle list format from CSV upload: [{"date": "...", "metric_name": "...", "value": ...}, ...]
            if isinstance(record.data, list):
                for row in record.data:
                    if isinstance(row, dict) and row.get("metric_name") == metric_name:
                        records.append({
                            "date": pd.to_datetime(row.get("date")),
                            "value": float(row.get("value", 0))
                        })
            # Handle dict format: {"date": "2024-01-01", "metrics": {...}}
            elif isinstance(record.data, dict):
                if metric_name in record.data.get("metrics", {}):
                    records.append({
                        "date": pd.to_datetime(record.data.get("date")),
                        "value": float(record.data["metrics"][metric_name])
                    })
    
    df = pd.DataFrame(records)
    
    if df.empty:
        raise ValueError(f"No data found for business_id={business_id}, metric={metric_name}")
    
    return df


def clean_timeseries_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare time-series data.
    
    Args:
        df: DataFrame with 'date' and 'value' columns
    
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    # Remove duplicates, keep latest
    df = df.drop_duplicates(subset=['date'], keep='last')
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    # Handle missing values - forward fill then backward fill
    df['value'] = df['value'].fillna(method='ffill').fillna(method='bfill')
    
    # Remove any remaining NaN values
    df = df.dropna()
    
    return df


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add date-based features.
    
    Args:
        df: DataFrame with 'date' column
    
    Returns:
        DataFrame with additional date features
    """
    df = df.copy()
    
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['year'] = df['date'].dt.year
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    
    return df


def add_lag_features(df: pd.DataFrame, lags: list = None) -> pd.DataFrame:
    """
    Add lagged features.
    
    Args:
        df: DataFrame with 'value' column
        lags: List of lag periods (default from config)
    
    Returns:
        DataFrame with lag features
    """
    df = df.copy()
    lags = lags or LAG_FEATURES
    
    for lag in lags:
        df[f'lag_{lag}'] = df['value'].shift(lag)
    
    return df


def add_rolling_features(df: pd.DataFrame, windows: list = None) -> pd.DataFrame:
    """
    Add rolling window features.
    
    Args:
        df: DataFrame with 'value' column
        windows: List of window sizes (default from config)
    
    Returns:
        DataFrame with rolling features
    """
    df = df.copy()
    windows = windows or ROLLING_WINDOWS
    
    for window in windows:
        df[f'rolling_mean_{window}'] = df['value'].rolling(window=window).mean()
        df[f'rolling_std_{window}'] = df['value'].rolling(window=window).std()
    
    return df


def prepare_data_for_xgboost(
    session: Session,
    business_id: int,
    metric_name: str
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare data for XGBoost training.
    
    Returns:
        Tuple of (features_df, target_series)
    """
    # Load and clean data
    df = load_timeseries_data(session, business_id, metric_name)
    df = clean_timeseries_data(df)
    
    # Add features
    df = add_date_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    
    # Drop rows with NaN (from lag/rolling features)
    df = df.dropna()
    
    if len(df) < MIN_TRAINING_SAMPLES:
        raise ValueError(
            f"Insufficient data: {len(df)} samples (minimum {MIN_TRAINING_SAMPLES} required)"
        )
    
    # Separate features and target
    feature_cols = [col for col in df.columns if col not in ['date', 'value']]
    X = df[feature_cols]
    y = df['value']
    
    return X, y


def prepare_data_for_prophet(
    session: Session,
    business_id: int,
    metric_name: str
) -> pd.DataFrame:
    """
    Prepare data for Prophet model (requires 'ds' and 'y' columns).
    
    Returns:
        DataFrame with 'ds' (date) and 'y' (value) columns
    """
    df = load_timeseries_data(session, business_id, metric_name)
    df = clean_timeseries_data(df)
    
    if len(df) < MIN_TRAINING_SAMPLES:
        raise ValueError(
            f"Insufficient data: {len(df)} samples (minimum {MIN_TRAINING_SAMPLES} required)"
        )
    
    # Prophet requires specific column names
    prophet_df = pd.DataFrame({
        'ds': df['date'],
        'y': df['value']
    })
    
    return prophet_df
