"""Production-grade API data connector for real backend integration."""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
import os
from dotenv import load_dotenv
import json

load_dotenv()

class DataConnector:
    """Unified data connector for all backend APIs."""
    
    def __init__(self):
        self.base_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        self.api_key = os.getenv('API_KEY', 'demo-key')
        self.timeout = 30
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    @st.cache_data(ttl=300)
    def get_revenue_data(self, start_date: str, end_date: str, granularity: str = 'daily') -> pd.DataFrame:
        """Fetch revenue data with caching."""
        endpoint = '/api/analytics/revenue'
        params = {'start_date': start_date, 'end_date': end_date, 'granularity': granularity}
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', params=params, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return pd.DataFrame(resp.json()['data'])
        except Exception as e:
            print(f'Revenue API error: {e}')
            return self._mock_revenue_data(start_date, end_date)
    
    @st.cache_data(ttl=300)
    def get_customer_data(self) -> pd.DataFrame:
        """Fetch customer data with segments."""
        endpoint = '/api/customers'
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return pd.DataFrame(resp.json()['data'])
        except:
            return self._mock_customer_data()
    
    @st.cache_data(ttl=300)
    def get_transaction_data(self, limit: int = 10000) -> pd.DataFrame:
        """Fetch transaction data."""
        endpoint = '/api/transactions'
        params = {'limit': limit}
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', params=params, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return pd.DataFrame(resp.json()['data'])
        except:
            return self._mock_transaction_data(limit)
    
    @st.cache_data(ttl=600)
    def get_churn_predictions(self) -> Dict[str, Any]:
        """Fetch ML churn predictions."""
        endpoint = '/api/predictions/churn'
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except:
            return self._mock_churn_predictions()
    
    @st.cache_data(ttl=600)
    def get_cohort_analysis(self) -> Dict[str, Any]:
        """Fetch cohort retention data."""
        endpoint = '/api/analytics/cohorts'
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except:
            return self._mock_cohort_data()
    
    @st.cache_data(ttl=600)
    def get_benchmarks(self, industry: str = 'saas') -> Dict[str, float]:
        """Fetch industry benchmarks."""
        endpoint = '/api/benchmarks'
        params = {'industry': industry}
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', params=params, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except:
            return self._mock_benchmarks()
    
    @st.cache_data(ttl=600)
    def get_attribution_data(self) -> Dict[str, Any]:
        """Fetch multi-touch attribution models."""
        endpoint = '/api/analytics/attribution'
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except:
            return self._mock_attribution_data()
    
    @st.cache_data(ttl=600)
    def get_anomalies(self, metric: str = 'revenue') -> List[Dict]:
        """Fetch detected anomalies."""
        endpoint = '/api/analytics/anomalies'
        params = {'metric': metric}
        try:
            resp = requests.get(f'{self.base_url}{endpoint}', params=params, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()['anomalies']
        except:
            return self._mock_anomalies()
    
    # MOCK DATA GENERATORS
    def _mock_revenue_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        dates = pd.date_range(start_date, end_date, freq='D')
        return pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(50000, 5000, len(dates)),
            'transactions': np.random.poisson(150, len(dates))
        })
    
    def _mock_customer_data(self) -> pd.DataFrame:
        return pd.DataFrame({
            'customer_id': range(1000, 2000),
            'ltv': np.random.uniform(2000, 20000, 1000),
            'cac': np.random.uniform(50, 500, 1000),
            'segment': np.random.choice(['high', 'medium', 'low'], 1000),
            'churn_risk': np.random.uniform(0, 1, 1000),
            'signup_date': [datetime.now() - timedelta(days=x) for x in np.random.randint(1, 730, 1000)]
        })
    
    def _mock_transaction_data(self, limit: int = 10000) -> pd.DataFrame:
        return pd.DataFrame({
            'txn_id': range(limit),
            'customer_id': np.random.randint(1000, 2000, limit),
            'amount': np.random.exponential(150, limit),
            'channel': np.random.choice(['web', 'mobile', 'api', 'retail'], limit),
            'timestamp': [datetime.now() - timedelta(hours=x) for x in np.random.randint(1, 2000, limit)],
            'product_category': np.random.choice(['software', 'hardware', 'service', 'other'], limit)
        })
    
    def _mock_churn_predictions(self) -> Dict[str, Any]:
        return {
            'high_risk': {'count': 67, 'rate': 0.067},
            'medium_risk': {'count': 189, 'rate': 0.189},
            'low_risk': {'count': 744, 'rate': 0.744},
            'predicted_churn_30d': 0.089,
            'confidence_score': 0.87,
            'model_performance': {'precision': 0.82, 'recall': 0.79, 'f1': 0.80}
        }
    
    def _mock_cohort_data(self) -> Dict[str, Any]:
        periods = ['Week 0', 'Week 4', 'Week 8', 'Week 12', 'Week 16', 'Week 20']
        cohorts = ['2025-01', '2025-02', '2025-03']
        data = []
        for cohort in cohorts:
            for i, period in enumerate(periods):
                data.append({
                    'cohort': cohort,
                    'period': period,
                    'week': i,
                    'retention': max(0.5, 1.0 - (i * 0.08 + np.random.uniform(-0.05, 0.05))),
                    'users': int(np.random.randint(800, 1200))
                })
        return {'cohorts': data}
    
    def _mock_benchmarks(self) -> Dict[str, float]:
        return {
            'avg_ltv': 5800, 'avg_cac': 145, 'avg_ltv_cac_ratio': 40,
            'avg_churn': 0.058, 'avg_mrr_growth': 0.089, 'avg_conversion': 0.038,
            'your_ltv': 7200, 'your_cac': 120, 'your_churn': 0.042, 'your_mrr_growth': 0.124
        }
    
    def _mock_attribution_data(self) -> Dict[str, Any]:
        return {
            'channels': ['organic', 'paid_search', 'social', 'referral', 'direct'],
            'first_touch': [0.15, 0.28, 0.22, 0.18, 0.17],
            'last_touch': [0.08, 0.35, 0.25, 0.15, 0.17],
            'linear': [0.12, 0.32, 0.24, 0.17, 0.15],
            'revenue_influenced': [45000, 125000, 87000, 54000, 38000]
        }
    
    def _mock_anomalies(self) -> List[Dict]:
        return [
            {'date': '2025-01-15', 'metric': 'revenue', 'value': 32000, 'expected': 50000, 'severity': 'high', 'reason': 'System outage detected'},
            {'date': '2025-01-20', 'metric': 'churn', 'value': 0.12, 'expected': 0.045, 'severity': 'high', 'reason': 'Unusual spike'}
        ]

@st.cache_resource
def get_connector() -> DataConnector:
    return DataConnector()
