import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json


@dataclass
class ModelMetrics:
    """
    Data class for storing model performance metrics at a specific point in time.
    """
    timestamp: datetime
    rmse: float
    mae: float
    mse: float
    r2_score: float
    n_samples: int
    prediction_drift: Optional[float] = None
    data_drift: Optional[float] = None
    
    def to_dict(self):
        """Convert metrics to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'rmse': self.rmse,
            'mae': self.mae,
            'mse': self.mse,
            'r2_score': self.r2_score,
            'n_samples': self.n_samples,
            'prediction_drift': self.prediction_drift,
            'data_drift': self.data_drift
        }


class ModelMonitor:
    """
    Comprehensive model monitoring system for tracking model performance,
    drift detection, and anomaly identification over time.
    
    Features:
    - Performance metric tracking (RMSE, MAE, MSE, R2)
    - Data drift detection using statistical tests
    - Prediction drift monitoring
    - Anomaly detection in predictions
    - Alert generation for degradation
    """
    
    def __init__(self, baseline_rmse: float, alert_threshold: float = 0.15):
        """
        Initialize model monitor.
        
        Args:
            baseline_rmse: Baseline RMSE for comparison
            alert_threshold: Percentage increase in RMSE to trigger alert (default: 15%)
        """
        self.baseline_rmse = baseline_rmse
        self.alert_threshold = alert_threshold
        self.metrics_history: List[ModelMetrics] = []
        self.alerts: List[Dict] = []
        self.drift_scores: List[Dict] = []
        
    def log_metrics(self, rmse: float, mae: float, mse: float, r2_score: float, 
                   n_samples: int, prediction_drift: Optional[float] = None,
                   data_drift: Optional[float] = None) -> ModelMetrics:
        """
        Log model performance metrics.
        
        Args:
            rmse: Root Mean Squared Error
            mae: Mean Absolute Error
            mse: Mean Squared Error
            r2_score: R-squared score
            n_samples: Number of samples evaluated
            prediction_drift: Drift score for predictions (optional)
            data_drift: Drift score for input data (optional)
            
        Returns:
            ModelMetrics object with logged data
        """
        metrics = ModelMetrics(
            timestamp=datetime.now(),
            rmse=rmse,
            mae=mae,
            mse=mse,
            r2_score=r2_score,
            n_samples=n_samples,
            prediction_drift=prediction_drift,
            data_drift=data_drift
        )
        
        self.metrics_history.append(metrics)
        
        # Check for performance degradation
        self._check_degradation(metrics)
        
        # Track drift
        if prediction_drift is not None or data_drift is not None:
            self.drift_scores.append({
                'timestamp': metrics.timestamp,
                'prediction_drift': prediction_drift,
                'data_drift': data_drift
            })
        
        return metrics
    
    def _check_degradation(self, metrics: ModelMetrics):
        """
        Check if model performance has degraded relative to baseline.
        
        Args:
            metrics: Current metrics
        """
        rmse_increase = (metrics.rmse - self.baseline_rmse) / self.baseline_rmse
        
        if rmse_increase > self.alert_threshold:
            alert = {
                'timestamp': metrics.timestamp,
                'type': 'performance_degradation',
                'severity': 'high' if rmse_increase > 0.30 else 'medium',
                'message': f'RMSE increased by {rmse_increase*100:.1f}%',
                'baseline_rmse': self.baseline_rmse,
                'current_rmse': metrics.rmse,
                'increase_percentage': rmse_increase * 100
            }
            self.alerts.append(alert)
    
    def detect_data_drift(self, current_data: np.ndarray, 
                         reference_data: np.ndarray,
                         method: str = 'ks') -> Tuple[float, bool]:
        """
        Detect data drift using statistical tests.
        
        Args:
            current_data: Recent input data
            reference_data: Baseline/training data
            method: 'ks' (Kolmogorov-Smirnov) or 'psi' (Population Stability Index)
            
        Returns:
            Tuple of (drift_score, is_drifted)
        """
        if method == 'ks':
            # Simplified KS test
            drift_score = np.abs(
                np.mean(current_data, axis=0) - np.mean(reference_data, axis=0)
            ) / (np.std(reference_data, axis=0) + 1e-10)
            is_drifted = np.any(drift_score > 2.0)  # 2 std deviations
            return float(np.max(drift_score)), is_drifted
        else:
            # PSI calculation
            bins = 10
            drift_score = 0
            for i in range(current_data.shape[1]):
                ref_counts = np.histogram(reference_data[:, i], bins=bins)[0]
                curr_counts = np.histogram(current_data[:, i], bins=bins)[0]
                
                # Avoid division by zero
                ref_props = (ref_counts + 1e-10) / (np.sum(ref_counts) + 1e-10)
                curr_props = (curr_counts + 1e-10) / (np.sum(curr_counts) + 1e-10)
                
                drift_score += np.sum(curr_props * np.log(curr_props / ref_props))
            
            is_drifted = drift_score > 0.1  # PSI threshold
            return drift_score, is_drifted
    
    def detect_prediction_anomalies(self, predictions: np.ndarray,
                                   residuals: np.ndarray,
                                   threshold_std: float = 3.0) -> Dict:
        """
        Detect anomalous predictions using residual analysis.
        
        Args:
            predictions: Model predictions
            residuals: Prediction residuals (y_true - y_pred)
            threshold_std: Number of standard deviations for anomaly threshold
            
        Returns:
            Dictionary with anomaly detection results
        """
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        
        # Find anomalies
        anomalies = np.abs(residuals - mean_residual) > threshold_std * std_residual
        anomaly_indices = np.where(anomalies)[0]
        
        return {
            'n_anomalies': len(anomaly_indices),
            'anomaly_rate': len(anomaly_indices) / len(residuals),
            'anomaly_indices': anomaly_indices.tolist(),
            'mean_residual': mean_residual,
            'std_residual': std_residual
        }
    
    def get_metrics_summary(self, hours: int = 24) -> pd.DataFrame:
        """
        Get summary of metrics over the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            DataFrame with metrics summary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return pd.DataFrame()
        
        data = [m.to_dict() for m in recent_metrics]
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.sort_values('timestamp')
    
    def get_alerts(self, hours: int = 24) -> List[Dict]:
        """
        Get alerts from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of alert dictionaries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            a for a in self.alerts
            if a['timestamp'] >= cutoff_time
        ]
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive monitoring report.
        
        Returns:
            Dictionary with monitoring summary
        """
        if not self.metrics_history:
            return {'status': 'no_data'}
        
        latest_metrics = self.metrics_history[-1]
        recent_metrics = self.get_metrics_summary(hours=24)
        recent_alerts = self.get_alerts(hours=24)
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'status': 'healthy' if not recent_alerts else 'degraded',
            'latest_metrics': latest_metrics.to_dict(),
            'metrics_24h_mean': recent_metrics.mean().to_dict() if len(recent_metrics) > 0 else {},
            'metrics_24h_min': recent_metrics.min().to_dict() if len(recent_metrics) > 0 else {},
            'metrics_24h_max': recent_metrics.max().to_dict() if len(recent_metrics) > 0 else {},
            'alert_count_24h': len(recent_alerts),
            'recent_alerts': recent_alerts[-10:],  # Last 10 alerts
            'total_samples_monitored': sum(m.n_samples for m in self.metrics_history)
        }
        
        return report
    
    def export_metrics(self, filepath: str):
        """
        Export metrics history to JSON file.
        
        Args:
            filepath: Path to export file
        """
        data = {
            'baseline_rmse': self.baseline_rmse,
            'metrics': [m.to_dict() for m in self.metrics_history],
            'alerts': self.alerts
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
