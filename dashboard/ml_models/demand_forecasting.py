import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class DemandForecaster:
    """
    Multi-method demand forecasting for product-level inventory planning.
    
    Combines time-series analysis (exponential smoothing) with machine learning
    (ensemble methods) for robust short-term and long-term demand forecasts.
    """
    
    def __init__(self, forecast_horizon: int = 30, random_state: int = 42):
        """
        Initialize demand forecaster.
        
        Args:
            forecast_horizon: Number of periods to forecast (default: 30 days)
            random_state: Random seed for reproducibility
        """
        self.forecast_horizon = forecast_horizon
        self.random_state = random_state
        
        # Time-series model
        self.ts_model = None
        self.ts_seasonal_period = None
        
        # ML models
        self.rf_model = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.gb_model = GradientBoostingRegressor(
            n_estimators=120,
            learning_rate=0.05,
            max_depth=6,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            subsample=0.8
        )
        
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.models_trained = False
        
    def create_features(self, series: pd.Series, lookback: int = 7) -> pd.DataFrame:
        """
        Create lagged and rolling features for ML models.
        
        Args:
            series: Time series data
            lookback: Number of previous periods to use as features
            
        Returns:
            DataFrame with engineered features
        """
        df = pd.DataFrame({'demand': series})
        
        # Lagged features
        for i in range(1, lookback + 1):
            df[f'demand_lag_{i}'] = df['demand'].shift(i)
        
        # Rolling statistics
        df['demand_rolling_mean_7'] = df['demand'].rolling(window=7).mean()
        df['demand_rolling_std_7'] = df['demand'].rolling(window=7).std()
        df['demand_rolling_mean_14'] = df['demand'].rolling(window=14).mean()
        df['demand_rolling_std_14'] = df['demand'].rolling(window=14).std()
        
        # Trend features
        df['time_trend'] = np.arange(len(df))
        df['day_of_week'] = series.index.dayofweek if hasattr(series.index, 'dayofweek') else 0
        df['day_of_month'] = series.index.day if hasattr(series.index, 'day') else 15
        
        # Remove NaN rows
        df = df.dropna()
        
        return df
    
    def train(self, demand_series: pd.Series) -> Dict:
        """
        Train both time-series and ML models.
        
        Args:
            demand_series: Historical demand data
            
        Returns:
            Dictionary with training metrics
        """
        # Train time-series model (exponential smoothing)
        try:
            self.ts_seasonal_period = 7  # Weekly seasonality
            self.ts_model = ExponentialSmoothing(
                demand_series,
                seasonal_periods=self.ts_seasonal_period,
                trend='add',
                seasonal='add',
                initialization_method='estimated'
            ).fit(optimized=True)
            ts_aic = self.ts_model.aic
        except:
            # Fallback to simpler model
            self.ts_model = ExponentialSmoothing(
                demand_series,
                trend='add'
            ).fit(optimized=True)
            ts_aic = self.ts_model.aic
        
        # Create features for ML models
        features_df = self.create_features(demand_series, lookback=7)
        X = features_df.drop('demand', axis=1).values
        y = features_df['demand'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest
        self.rf_model.fit(X_scaled, y)
        rf_preds = self.rf_model.predict(X_scaled)
        rf_rmse = np.sqrt(mean_squared_error(y, rf_preds))
        
        # Train Gradient Boosting
        self.gb_model.fit(X_scaled, y)
        gb_preds = self.gb_model.predict(X_scaled)
        gb_rmse = np.sqrt(mean_squared_error(y, gb_preds))
        
        # Feature importance (ensemble average)
        importances = (self.rf_model.feature_importances_ + 
                      self.gb_model.feature_importances_) / 2
        feature_names = [f'demand_lag_{i}' for i in range(1, 8)] + \
                       ['demand_rolling_mean_7', 'demand_rolling_std_7',
                        'demand_rolling_mean_14', 'demand_rolling_std_14',
                        'time_trend', 'day_of_week', 'day_of_month']
        
        self.feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        self.models_trained = True
        
        return {
            'ts_aic': ts_aic,
            'rf_rmse': rf_rmse,
            'gb_rmse': gb_rmse,
            'ensemble_rmse': (rf_rmse + gb_rmse) / 2
        }
    
    def forecast(self, demand_series: pd.Series, 
                forecast_type: str = 'ensemble') -> np.ndarray:
        """
        Generate demand forecast for next N periods.
        
        Args:
            demand_series: Recent demand history
            forecast_type: 'ts' (time-series), 'ml' (machine learning), or 'ensemble'
            
        Returns:
            Forecast array of length forecast_horizon
        """
        if not self.models_trained:
            self.train(demand_series)
        
        if forecast_type == 'ts':
            return self._forecast_ts(demand_series)
        elif forecast_type == 'ml':
            return self._forecast_ml(demand_series)
        else:  # ensemble
            ts_forecast = self._forecast_ts(demand_series)
            ml_forecast = self._forecast_ml(demand_series)
            return (ts_forecast + ml_forecast) / 2
    
    def _forecast_ts(self, demand_series: pd.Series) -> np.ndarray:
        """
        Generate forecast using time-series model.
        """
        forecast = self.ts_model.forecast(steps=self.forecast_horizon)
        return np.maximum(forecast.values, 0)  # Ensure non-negative
    
    def _forecast_ml(self, demand_series: pd.Series) -> np.ndarray:
        """
        Generate forecast using ML models.
        """
        # Create features from recent data
        features_df = self.create_features(demand_series, lookback=7)
        latest_features = features_df.iloc[-1].drop('demand').values.reshape(1, -1)
        latest_features = self.scaler.transform(latest_features)
        
        # Generate rolling forecasts
        forecast = []
        current_features = latest_features.copy()
        
        for _ in range(self.forecast_horizon):
            # Ensemble prediction
            rf_pred = self.rf_model.predict(current_features)[0]
            gb_pred = self.gb_model.predict(current_features)[0]
            pred = max((rf_pred + gb_pred) / 2, 0)  # Ensure non-negative
            forecast.append(pred)
            
            # Update features for next period (simplified rolling)
            current_features[0, 0] = pred
        
        return np.array(forecast)
    
    def forecast_with_intervals(self, demand_series: pd.Series,
                               confidence: float = 0.95) -> Dict:
        """
        Forecast with confidence intervals.
        
        Args:
            demand_series: Recent demand history
            confidence: Confidence level for intervals
            
        Returns:
            Dictionary with forecast and interval bounds
        """
        forecast = self.forecast(demand_series, forecast_type='ensemble')
        
        # Estimate uncertainty (simplified using historical variance)
        residuals = demand_series.values[-30:] - np.mean(demand_series.values[-30:])
        std_error = np.std(residuals) * np.sqrt(1 + np.arange(self.forecast_horizon) / 10)
        
        # Confidence interval multiplier (z-score for 95% is ~1.96)
        z_score = 1.96 if confidence == 0.95 else 1.645 if confidence == 0.90 else 1.0
        margin = z_score * std_error
        
        return {
            'forecast': forecast,
            'upper_bound': forecast + margin,
            'lower_bound': np.maximum(forecast - margin, 0),  # Non-negative
            'std_error': std_error
        }
    
    def get_feature_importance(self, top_k: int = 10) -> pd.DataFrame:
        """
        Get top K important features for demand prediction.
        """
        if self.feature_importance is None:
            raise ValueError("Model not trained yet.")
        return self.feature_importance.head(top_k)
    
    def evaluate(self, demand_series: pd.Series, 
                test_size: int = 7) -> Dict:
        """
        Evaluate forecast accuracy on test period.
        
        Args:
            demand_series: Full demand history
            test_size: Number of periods to use for testing
            
        Returns:
            Dictionary with evaluation metrics
        """
        train_series = demand_series.iloc[:-test_size]
        test_series = demand_series.iloc[-test_size:]
        
        if not self.models_trained:
            self.train(train_series)
        
        forecast = self.forecast(train_series, forecast_type='ensemble')[:test_size]
        
        return {
            'rmse': np.sqrt(mean_squared_error(test_series, forecast)),
            'mae': mean_absolute_error(test_series, forecast),
            'mape': np.mean(np.abs((test_series - forecast) / test_series)) * 100,
            'r2': r2_score(test_series, forecast)
        }
