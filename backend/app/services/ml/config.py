"""Configuration settings for ML models and training."""

import os
from pathlib import Path

# Model storage paths
BASE_DIR = Path(__file__).parent
MODELS_STORE_DIR = BASE_DIR / "models_store"
MODELS_STORE_DIR.mkdir(exist_ok=True)

# XGBoost configuration
XGBOOST_CONFIG = {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "objective": "reg:squarederror",
    "random_state": 42,
}

# Prophet configuration
PROPHET_CONFIG = {
    "changepoint_prior_scale": 0.05,
    "seasonality_prior_scale": 10.0,
    "seasonality_mode": "multiplicative",
    "daily_seasonality": False,
    "weekly_seasonality": True,
    "yearly_seasonality": True,
}

# Feature engineering
LAG_FEATURES = [1, 7, 14, 30]  # Lag days
ROLLING_WINDOWS = [7, 14, 30]  # Rolling average windows

# Forecast settings
MIN_TRAINING_SAMPLES = 30  # Minimum data points required for training
TRAIN_TEST_SPLIT = 0.8  # Train/test split ratio

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1000
