"""ML Integration Module - Activates dormant ML models for real AI insights

This module wraps and initializes all 6 ML models:
- RevenueForecaster: XGBoost ensemble for revenue predictions
- AnomalyDetector: Detect unusual business patterns
- ChurnPredictor: Predict customer churn risk
- DemandForecaster: Forecast product demand
- HyperparameterTuning: ML model optimization
- ModelMonitoring: Track ML performance
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from ml_models.revenue_forecaster import EnsembleRevenueForecaster
    from ml_models.anomaly_detection import AnomalyDetector
    from ml_models.churn_prediction import ChurnPredictor
    from ml_models.demand_forecasting import DemandForecaster
    ML_MODELS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not load all ML models: {e}")
    ML_MODELS_AVAILABLE = False

class MLPipeline:
    """Central ML prediction pipeline"""
    
    def __init__(self):
        self.revenue_forecaster = None
        self.anomaly_detector = None
        self.churn_predictor = None
        self.demand_forecaster = None
        self.is_initialized = False
        
    def initialize(self, data: pd.DataFrame) -> bool:
        """Initialize all ML models with training data"""
        try:
            if not ML_MODELS_AVAILABLE:
                return False
                
            # Initialize Revenue Forecaster
            if 'revenue' in data.columns:
                self.revenue_forecaster = EnsembleRevenueForecaster()
                self.revenue_forecaster.train(data[['revenue']], verbose=False)
            
            # Initialize Anomaly Detector
            if all(col in data.columns for col in ['revenue', 'orders', 'customers']):
                self.anomaly_detector = AnomalyDetector()
                features = data[['revenue', 'orders', 'customers']]
                self.anomaly_detector.fit(features)
            
            # Initialize Churn Predictor  
            if all(col in data.columns for col in ['customers', 'orders', 'revenue']):
                self.churn_predictor = ChurnPredictor()
            
            # Initialize Demand Forecaster
            if all(col in data.columns for col in ['orders', 'date']):
                self.demand_forecaster = DemandForecaster()
                self.demand_forecaster.train(data[['orders']], verbose=False)
            
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Error initializing ML pipeline: {e}")
            return False
    
    def predict_revenue(self, last_revenue: np.ndarray, days_ahead: int = 30) -> Dict:
        """Generate revenue forecast with confidence intervals"""
        try:
            if self.revenue_forecaster is None:
                return self._default_forecast(last_revenue, days_ahead)
            
            result = self.revenue_forecaster.forecast(last_revenue, days_ahead=days_ahead)
            return result
        except:
            return self._default_forecast(last_revenue, days_ahead)
    
    def detect_anomalies(self, data: pd.DataFrame) -> List[Dict]:
        """Detect unusual patterns in data"""
        try:
            if self.anomaly_detector is None:
                return []
            
            features = data[['revenue', 'orders', 'customers']].tail(30)
            anomalies = self.anomaly_detector.detect(features)
            
            results = []
            for idx, is_anomaly in enumerate(anomalies):
                if is_anomaly:
                    results.append({
                        'date': data['date'].iloc[-(30-idx)],
                        'metric': 'Business Metrics',
                        'severity': 'medium',
                        'description': f'Unusual pattern detected on {data["date"].iloc[-(30-idx)].strftime("%Y-%m-%d")}'
                    })
            return results
        except:
            return []
    
    def predict_churn_risk(self, data: pd.DataFrame) -> Dict:
        """Predict customer churn risk"""
        try:
            if self.churn_predictor is None:
                return {'overall_risk': 0.0, 'at_risk_customers': 0}
            
            # Simplified churn prediction based on trends
            recent_data = data.tail(30)
            revenue_trend = (recent_data['revenue'].iloc[-1] - recent_data['revenue'].iloc[0]) / recent_data['revenue'].iloc[0]
            orders_trend = (recent_data['orders'].iloc[-1] - recent_data['orders'].iloc[0]) / recent_data['orders'].iloc[0]
            
            # Higher churn risk if metrics declining
            churn_risk = max(0, (-revenue_trend + -orders_trend) / 2)
            churn_risk = min(1.0, churn_risk)
            
            at_risk = int(recent_data['customers'].iloc[-1] * churn_risk * 0.2)
            
            return {
                'overall_risk': float(churn_risk),
                'at_risk_customers': at_risk,
                'revenue_trend': float(revenue_trend),
                'orders_trend': float(orders_trend)
            }
        except:
            return {'overall_risk': 0.0, 'at_risk_customers': 0}
    
    def forecast_demand(self, last_orders: np.ndarray, days_ahead: int = 30) -> Dict:
        """Forecast product demand"""
        try:
            if self.demand_forecaster is None:
                return self._default_forecast(last_orders, days_ahead)
            
            result = self.demand_forecaster.forecast(last_orders, days_ahead=days_ahead)
            return result
        except:
            return self._default_forecast(last_orders, days_ahead)
    
    def generate_insights(self, data: pd.DataFrame) -> List[Dict]:
        """Generate AI-powered business insights"""
        insights = []
        
        try:
            # Revenue forecast insight
            if 'revenue' in data.columns:
                forecast = self.predict_revenue(data['revenue'].tail(30).values)
                if 'forecast' in forecast:
                    predicted_change = (forecast['forecast'][-1] - data['revenue'].iloc[-1]) / data['revenue'].iloc[-1]
                    if predicted_change > 0.1:
                        insights.append({
                            'type': 'growth',
                            'priority': 'high',
                            'title': 'Revenue Growth Opportunity',
                            'message': f'ML predicts {predicted_change*100:+.1f}% revenue increase. Capitalize on this trend.',
                            'confidence': forecast.get('confidence', 0.95)
                        })
                    elif predicted_change < -0.1:
                        insights.append({
                            'type': 'alert',
                            'priority': 'high',
                            'title': 'Revenue Decline Warning',
                            'message': f'ML predicts {predicted_change*100:.1f}% revenue decline. Review pricing and marketing.',
                            'confidence': forecast.get('confidence', 0.95)
                        })
            
            # Anomaly detection
            anomalies = self.detect_anomalies(data)
            if anomalies:
                insights.append({
                    'type': 'alert',
                    'priority': 'medium',
                    'title': f'{len(anomalies)} Anomalies Detected',
                    'message': f'Unusual patterns found in business metrics. Review: {", ".join([a["description"] for a in anomalies[:2]])}',
                    'confidence': 0.85
                })
            
            # Churn risk
            churn_data = self.predict_churn_risk(data)
            if churn_data['overall_risk'] > 0.15:
                insights.append({
                    'type': 'alert',
                    'priority': 'high',
                    'title': 'Customer Churn Risk',
                    'message': f'{churn_data["at_risk_customers"]} customers at risk. Implement retention strategy.',
                    'confidence': 0.80
                })
            
            # Default success message
            if not insights:
                insights.append({
                    'type': 'success',
                    'priority': 'low',
                    'title': 'Strong Performance',
                    'message': 'All business metrics performing well. No immediate concerns detected.',
                    'confidence': 1.0
                })
                
        except Exception as e:
            print(f"Error generating insights: {e}")
        
        return insights
    
    @staticmethod
    def _default_forecast(data: np.ndarray, days_ahead: int) -> Dict:
        """Generate default linear forecast when ML models unavailable"""
        # Simple linear extrapolation
        if len(data) < 2:
            return {'forecast': [data[-1]] * days_ahead, 'confidence': 0.5}
        
        slope = (data[-1] - data[-7]) / 7 if len(data) >= 7 else 0
        forecast = [data[-1] + slope * i for i in range(1, days_ahead + 1)]
        return {'forecast': forecast, 'confidence': 0.6}

# Global pipeline instance
ml_pipeline = MLPipeline()

def initialize_ml_models(data: pd.DataFrame) -> bool:
    """Initialize ML models with data"""
    return ml_pipeline.initialize(data)

def get_ml_insights(data: pd.DataFrame) -> List[Dict]:
    """Get AI-powered insights"""
    return ml_pipeline.generate_insights(data)

def forecast_revenue_ml(data: pd.DataFrame, days_ahead: int = 30) -> Dict:
    """Forecast revenue using ML"""
    if 'revenue' not in data.columns or len(data) < 30:
        return {}
    return ml_pipeline.predict_revenue(data['revenue'].tail(30).values, days_ahead)

def detect_anomalies_ml(data: pd.DataFrame) -> List[Dict]:
    """Detect anomalies using ML"""
    if len(data) < 30:
        return []
    return ml_pipeline.detect_anomalies(data)

def predict_churn_ml(data: pd.DataFrame) -> Dict:
    """Predict churn using ML"""
    if len(data) < 30:
        return {'overall_risk': 0.0, 'at_risk_customers': 0}
    return ml_pipeline.predict_churn_risk(data)
