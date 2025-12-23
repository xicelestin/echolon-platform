"""Custom ML Features Module - Industry-specific metrics

Features:
- Custom business metrics calculation
- Industry-specific feature engineering
- Seasonal adjustments
- Trend analysis
- Performance benchmarking
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class CustomFeatureEngine:
    """Generate custom industry-specific features"""
    
    def __init__(self):
        self.features_calculated = {}
    
    def calculate_customer_lifetime_value(self, df):
        """Calculate customer lifetime value metrics"""
        if 'revenue' not in df.columns or 'customers' not in df.columns:
            return {}
        
        total_revenue = df['revenue'].sum()
        total_customers = df['customers'].iloc[-1]
        
        clv = total_revenue / total_customers if total_customers > 0 else 0
        
        return {
            'clv': float(clv),
            'clv_trend': self._calculate_trend(df['revenue'].values) if len(df) > 1 else 0
        }
    
    def calculate_seasonality_index(self, df, period=30):
        """Calculate seasonality index"""
        if 'revenue' not in df.columns or len(df) < period * 2:
            return 0
        
        data = df['revenue'].values
        seasonal_avg = np.mean(data[-period:])
        overall_avg = np.mean(data)
        
        seasonality = (seasonal_avg / overall_avg - 1) * 100 if overall_avg > 0 else 0
        return float(seasonality)
    
    def calculate_customer_acquisition_cost(self, df):
        """Calculate CAC"""
        if 'marketing_spend' not in df.columns or 'new_customers' not in df.columns:
            return 0
        
        total_spend = df['marketing_spend'].sum()
        total_new = df['new_customers'].sum()
        
        cac = total_spend / total_new if total_new > 0 else 0
        return float(cac)
    
    def calculate_revenue_concentration(self, df):
        """Calculate revenue concentration (80/20 analysis)"""
        if 'revenue' not in df.columns:
            return 0
        
        revenues = np.sort(df['revenue'].values)[::-1]
        cumsum = np.cumsum(revenues)
        total = cumsum[-1]
        
        if total == 0:
            return 0
        
        idx_80 = np.argmax(cumsum >= total * 0.8)
        concentration = (idx_80 + 1) / len(revenues) * 100
        
        return float(concentration)
    
    def calculate_volatility(self, df):
        """Calculate revenue volatility (coefficient of variation)"""
        if 'revenue' not in df.columns:
            return 0
        
        revenue = df['revenue'].values
        if len(revenue) < 2 or np.mean(revenue) == 0:
            return 0
        
        cv = (np.std(revenue) / np.mean(revenue)) * 100
        return float(cv)
    
    def calculate_customer_retention_rate(self, df):
        """Estimate customer retention rate"""
        if 'customers' not in df.columns or len(df) < 2:
            return 0
        
        customers = df['customers'].values
        if len(customers) < 2:
            return 100
        
        retention_rate = (customers[-1] / customers[-2]) * 100 if customers[-2] > 0 else 100
        return float(min(100, retention_rate))
    
    def calculate_all_custom_features(self, df):
        """Calculate all custom features"""
        return {
            'clv_metrics': self.calculate_customer_lifetime_value(df),
            'seasonality_index': self.calculate_seasonality_index(df),
            'cac': self.calculate_customer_acquisition_cost(df),
            'revenue_concentration': self.calculate_revenue_concentration(df),
            'volatility': self.calculate_volatility(df),
            'retention_rate': self.calculate_customer_retention_rate(df)
        }
    
    def _calculate_trend(self, data):
        """Calculate linear trend"""
        if len(data) < 2:
            return 0
        x = np.arange(len(data))
        z = np.polyfit(x, data, 1)
        return float(z[0])

# Global instance
feature_engine = CustomFeatureEngine()

def get_custom_features(df):
    """Get all custom features for data"""
    return feature_engine.calculate_all_custom_features(df)

def get_feature_insights(df):
    """Generate insights from custom features"""
    features = get_custom_features(df)
    insights = []
    
    if features['volatility'] > 30:
        insights.append(f"⚠️ High Revenue Volatility: {features['volatility']:.1f}%")
    
    if features['seasonality_index'] > 15:
        insights.append(f"📈 Strong Seasonality Detected: {features['seasonality_index']:.1f}%")
    
    if features['retention_rate'] < 80:
        insights.append(f"👥 Low Retention Rate: {features['retention_rate']:.1f}%")
    
    return insights
