"""ML Model Monitoring - Track drift and performance

Features:
- Model performance tracking
- Data drift detection
- Prediction monitoring
- Alert generation
- Performance reports
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List

class ModelMonitor:
    """Monitor ML models for drift and performance degradation"""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.monitoring_history = []
        self.drift_threshold = 0.15  # 15% deviation
        self.performance_threshold = 0.85  # 85% of baseline
    
    def set_baseline(self, metrics: Dict):
        """Set baseline metrics for comparison"""
        self.baseline_metrics = metrics
        return True
    
    def detect_data_drift(self, current_data: pd.DataFrame, baseline_data: pd.DataFrame) -> Dict:
        """Detect data drift using statistical tests"""
        drift_detected = {}
        numeric_cols = current_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col not in baseline_data.columns:
                continue
            
            baseline_mean = baseline_data[col].mean()
            baseline_std = baseline_data[col].std()
            current_mean = current_data[col].mean()
            
            if baseline_std > 0:
                z_score = abs((current_mean - baseline_mean) / baseline_std)
                if z_score > 2.0:  # 2-sigma drift
                    drift_detected[col] = {
                        'baseline_mean': float(baseline_mean),
                        'current_mean': float(current_mean),
                        'z_score': float(z_score),
                        'drifted': True
                    }
        
        return drift_detected
    
    def monitor_prediction_performance(self, predictions: List[float], actuals: List[float]) -> Dict:
        """Monitor prediction performance"""
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        mae = np.mean(np.abs(predictions - actuals))
        mape = np.mean(np.abs((actuals - predictions) / (np.abs(actuals) + 1e-10))) * 100
        
        return {
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'baseline_rmse': self.baseline_metrics.get('rmse', rmse),
            'performance_degradation': float((rmse / self.baseline_metrics.get('rmse', rmse) - 1) * 100) if 'rmse' in self.baseline_metrics else 0
        }
    
    def generate_alerts(self, drift_metrics: Dict, perf_metrics: Dict) -> List[Dict]:
        """Generate alerts based on monitoring metrics"""
        alerts = []
        
        # Check for data drift
        if drift_metrics:
            drifted_cols = [col for col, metrics in drift_metrics.items() if metrics.get('drifted')]
            if drifted_cols:
                alerts.append({
                    'severity': 'high',
                    'type': 'data_drift',
                    'message': f'Data drift detected in: {" , ".join(drifted_cols)}',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check for performance degradation
        if perf_metrics['performance_degradation'] > 10:
            alerts.append({
                'severity': 'high',
                'type': 'performance_degradation',
                'message': f'Model performance degraded by {perf_metrics["performance_degradation"]:.1f}%',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def log_monitoring_event(self, event: Dict):
        """Log monitoring event"""
        event['timestamp'] = datetime.now().isoformat()
        self.monitoring_history.append(event)
    
    def get_monitoring_report(self) -> Dict:
        """Generate monitoring report"""
        if not self.monitoring_history:
            return {'status': 'no_monitoring_data'}
        
        return {
            'total_events': len(self.monitoring_history),
            'recent_events': self.monitoring_history[-5:],
            'baseline_metrics': self.baseline_metrics
        }

monitor = ModelMonitor()

def setup_model_monitoring(baseline_metrics: Dict):
    """Setup monitoring with baseline metrics"""
    monitor.set_baseline(baseline_metrics)
    return True

def check_model_health(current_data: pd.DataFrame, baseline_data: pd.DataFrame) -> Dict:
    """Check overall model health"""
    drift = monitor.detect_data_drift(current_data, baseline_data)
    alerts = monitor.generate_alerts(drift, {})
    
    return {
        'drifted_features': len(drift),
        'alerts': alerts,
        'health_status': 'healthy' if not alerts else 'degraded'
    }
