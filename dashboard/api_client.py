"""
Backend API Client for Echolon AI Dashboard
Handles all communication with backend services for ML models and data processing
"""

import requests
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os


class APIClient:
    """Client for connecting to Echolon backend services"""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Backend API base URL (defaults to env var ECHOLON_API_URL)
            api_key: API key for authentication (defaults to env var ECHOLON_API_KEY)
        """
        self.base_url = base_url or os.getenv('ECHOLON_API_URL', 'http://localhost:8000')
        self.api_key = api_key or os.getenv('ECHOLON_API_KEY', '')
        self.timeout = 30
        
        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip('/')
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        return headers
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to backend API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/api/insights')
            data: Request body data
            params: URL query parameters
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise APIError("Request timed out - backend service not responding")
        except requests.exceptions.ConnectionError:
            raise APIError(f"Cannot connect to backend at {self.base_url}")
        except requests.exceptions.HTTPError as e:
            raise APIError(f"API returned error {response.status_code}: {response.text}")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")
    
    def upload_csv_data(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """
        Upload CSV data to backend for processing
        
        Args:
            dataframe: Pandas DataFrame with CSV data
            
        Returns:
            Response with processing results
        """
        # Convert dataframe to records format
        data = dataframe.to_dict(orient='records')
        
        payload = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'row_count': len(dataframe),
            'columns': list(dataframe.columns)
        }
        
        return self._make_request('POST', '/api/upload', data=payload)
    
    def get_insights(self, data_source: str = 'demo') -> Dict[str, Any]:
        """
        Fetch AI-generated business insights
        
        Args:
            data_source: 'demo' or 'uploaded'
            
        Returns:
            Insights data
        """
        params = {
            'data_source': data_source
        }
        
        return self._make_request('GET', '/api/insights', params=params)
    
    def get_predictions(
        self, 
        metric: str, 
        horizon: str,
        data_source: str = 'demo'
    ) -> Dict[str, Any]:
        """
        Generate ML predictions
        
        Args:
            metric: Metric to predict (e.g., 'Revenue', 'Customer Growth')
            horizon: Prediction timeframe (e.g., '1 Month', '3 Months')
            data_source: 'demo' or 'uploaded'
            
        Returns:
            Predictions data
        """
        payload = {
            'metric': metric,
            'horizon': horizon,
            'data_source': data_source,
            'timestamp': datetime.now().isoformat()
        }
        
        return self._make_request('POST', '/api/predictions', data=payload)
    
    def health_check(self) -> bool:
        """
        Check if backend API is healthy
        
        Returns:
            True if backend is responding
        """
        try:
            response = self._make_request('GET', '/health')
            return response.get('status') == 'healthy'
        except:
            return False


class APIError(Exception):
    """Custom exception for API errors"""
    pass


# Mock implementations for testing without backend
class MockAPIClient(APIClient):
    """Mock client for testing without real backend"""
    
    def __init__(self):
        super().__init__()
        self.mock_mode = True
        
    def upload_csv_data(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """Mock CSV upload"""
        return {
            'status': 'success',
            'message': 'Data processed successfully (mock)',
            'row_count': len(dataframe),
            'processed_at': datetime.now().isoformat()
        }
    
    def get_insights(self, data_source: str = 'demo') -> Dict[str, Any]:
        """Mock insights"""
        return {
            'insights': [
                {
                    'category': 'Revenue Trends',
                    'title': 'Strong monthly growth',
                    'description': 'Revenue increased 12.5% over last month',
                    'confidence': 0.92
                },
                {
                    'category': 'Customer Behavior',
                    'title': 'Improved conversion rate',
                    'description': 'Conversion rate up 0.5 percentage points',
                    'confidence': 0.88
                },
                {
                    'category': 'Risk Alert',
                    'title': 'Average order value declining',
                    'description': 'AOV down 2.1% - investigate pricing strategy',
                    'confidence': 0.85
                }
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    def get_predictions(
        self, 
        metric: str, 
        horizon: str,
        data_source: str = 'demo'
    ) -> Dict[str, Any]:
        """Mock predictions"""
        # Generate mock prediction data
        base_value = 100000
        periods = {'1 Month': 1, '3 Months': 3, '6 Months': 6}
        num_periods = periods.get(horizon, 3)
        
        predictions = []
        for i in range(num_periods):
            predictions.append({
                'period': f'Month {i+1}',
                'predicted_value': base_value * (1.05 ** (i+1)),
                'confidence_lower': base_value * (1.03 ** (i+1)),
                'confidence_upper': base_value * (1.07 ** (i+1))
            })
        
        return {
            'metric': metric,
            'horizon': horizon,
            'predictions': predictions,
            'model_accuracy': 0.87,
            'generated_at': datetime.now().isoformat()
        }
    
    def health_check(self) -> bool:
        """Mock health check"""
        return True
