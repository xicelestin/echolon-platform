import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import RobustScaler
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """
    Multi-method anomaly detection for business metrics and transactions.
    
    Combines statistical methods, ensemble techniques, and density estimation
    for robust detection of unusual patterns in business data.
    """
    
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies (default: 0.05)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        
        # Ensemble models
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            n_estimators=100,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.elliptic_envelope = EllipticEnvelope(
            contamination=contamination,
            random_state=random_state
        )
        
        self.scaler = RobustScaler()
        self.is_fitted = False
        
    def fit(self, X: np.ndarray) -> Dict:
        """
        Fit anomaly detection models.
        
        Args:
            X: Training data (n_samples, n_features)
            
        Returns:
            Dictionary with fitting summary
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit Isolation Forest
        self.isolation_forest.fit(X_scaled)
        if_outliers = self.isolation_forest.predict(X_scaled)
        if_anomaly_score = self.isolation_forest.score_samples(X_scaled)
        
        # Fit Elliptic Envelope
        try:
            self.elliptic_envelope.fit(X_scaled)
            ee_outliers = self.elliptic_envelope.predict(X_scaled)
            ee_anomaly_score = self.elliptic_envelope.score_samples(X_scaled)
        except:
            ee_outliers = np.ones(len(X))
            ee_anomaly_score = np.zeros(len(X))
        
        self.is_fitted = True
        
        return {
            'n_samples': len(X),
            'n_features': X.shape[1],
            'if_anomalies': np.sum(if_outliers == -1),
            'ee_anomalies': np.sum(ee_outliers == -1),
            'contamination': self.contamination
        }
    
    def predict(self, X: np.ndarray, method: str = 'ensemble') -> np.ndarray:
        """
        Predict anomalies (-1 for anomaly, 1 for normal).
        
        Args:
            X: Data to score
            method: 'isolation_forest', 'elliptic', or 'ensemble' (default)
            
        Returns:
            Predictions array (-1 for anomaly, 1 for normal)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(X)
        
        if method == 'isolation_forest':
            return self.isolation_forest.predict(X_scaled)
        elif method == 'elliptic':
            return self.elliptic_envelope.predict(X_scaled)
        else:  # ensemble
            if_pred = self.isolation_forest.predict(X_scaled)
            ee_pred = self.elliptic_envelope.predict(X_scaled)
            # Ensemble: flag as anomaly if both methods agree
            ensemble_pred = np.where((if_pred == -1) & (ee_pred == -1), -1, 1)
            return ensemble_pred
    
    def anomaly_scores(self, X: np.ndarray) -> np.ndarray:
        """
        Get normalized anomaly scores (0-1, higher = more anomalous).
        
        Args:
            X: Data to score
            
        Returns:
            Anomaly scores in range [0, 1]
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(X)
        
        # Get raw scores from both methods
        if_scores = -self.isolation_forest.score_samples(X_scaled)  # Negate for higher = more anomalous
        ee_scores = -self.elliptic_envelope.score_samples(X_scaled)
        
        # Normalize to [0, 1]
        if_scores_norm = (if_scores - if_scores.min()) / (if_scores.max() - if_scores.min() + 1e-10)
        ee_scores_norm = (ee_scores - ee_scores.min()) / (ee_scores.max() - ee_scores.min() + 1e-10)
        
        # Ensemble average
        ensemble_scores = (if_scores_norm + ee_scores_norm) / 2
        
        return np.clip(ensemble_scores, 0, 1)
    
    def detect_with_scores(self, X: np.ndarray, 
                          threshold: float = 0.7) -> pd.DataFrame:
        """
        Detect anomalies with detailed scoring information.
        
        Args:
            X: Data to analyze
            threshold: Anomaly score threshold (default: 0.7)
            
        Returns:
            DataFrame with predictions and scores
        """
        predictions = self.predict(X, method='ensemble')
        scores = self.anomaly_scores(X)
        
        result = pd.DataFrame({
            'anomaly_score': scores,
            'is_anomaly': scores >= threshold,
            'prediction': predictions == -1,
            'risk_level': pd.cut(
                scores,
                bins=[0, 0.4, 0.7, 1.0],
                labels=['Low', 'Medium', 'High']
            )
        })
        
        return result
    
    def statistical_anomalies(self, series: pd.Series, 
                             n_std: float = 3.0) -> np.ndarray:
        """
        Detect anomalies using statistical methods (Z-score).
        
        Args:
            series: Time series or column data
            n_std: Number of standard deviations for threshold
            
        Returns:
            Boolean array indicating anomalies
        """
        z_scores = np.abs(stats.zscore(series.dropna()))
        return z_scores > n_std
    
    def temporal_anomalies(self, df: pd.DataFrame, 
                          time_col: str,
                          value_col: str,
                          window: int = 7) -> Dict:
        """
        Detect anomalies with temporal context.
        
        Args:
            df: DataFrame with time series data
            time_col: Column name for timestamps
            value_col: Column name for values
            window: Rolling window size (default: 7)
            
        Returns:
            Dictionary with temporal anomaly analysis
        """
        df_copy = df.copy()
        
        # Rolling statistics
        df_copy['rolling_mean'] = df_copy[value_col].rolling(window).mean()
        df_copy['rolling_std'] = df_copy[value_col].rolling(window).std()
        
        # Z-score relative to rolling window
        df_copy['rolling_zscore'] = np.abs(
            (df_copy[value_col] - df_copy['rolling_mean']) / (df_copy['rolling_std'] + 1e-10)
        )
        
        # Detect anomalies (zscore > 3)
        df_copy['is_anomaly'] = df_copy['rolling_zscore'] > 3.0
        
        return {
            'n_anomalies': df_copy['is_anomaly'].sum(),
            'anomaly_rate': df_copy['is_anomaly'].mean(),
            'results': df_copy[[time_col, value_col, 'rolling_mean', 'rolling_std', 'rolling_zscore', 'is_anomaly']]
        }
    
    def get_anomalous_samples(self, X: np.ndarray,
                             method: str = 'ensemble',
                             top_n: Optional[int] = None) -> np.ndarray:
        """
        Get indices of most anomalous samples.
        
        Args:
            X: Data to analyze
            method: Detection method
            top_n: Return top N anomalies (default: return all)
            
        Returns:
            Sorted indices of anomalous samples
        """
        scores = self.anomaly_scores(X)
        anomaly_indices = np.argsort(scores)[::-1]  # Sort descending
        
        if top_n:
            return anomaly_indices[:top_n]
        else:
            predictions = self.predict(X, method=method)
            return np.where(predictions == -1)[0][np.argsort(scores[predictions == -1])[::-1]]
    
    def summarize(self, X: np.ndarray) -> Dict:
        """
        Generate anomaly detection summary.
        
        Args:
            X: Data to analyze
            
        Returns:
            Summary dictionary
        """
        predictions = self.predict(X, method='ensemble')
        scores = self.anomaly_scores(X)
        
        return {
            'total_samples': len(X),
            'n_anomalies': np.sum(predictions == -1),
            'anomaly_rate': np.sum(predictions == -1) / len(X),
            'mean_anomaly_score': np.mean(scores),
            'max_anomaly_score': np.max(scores),
            'min_anomaly_score': np.min(scores),
            'anomaly_score_std': np.std(scores)
        }
