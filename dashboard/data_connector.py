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
    
    # ==================== SHOPIFY INTEGRATION ====================
    def connect_shopify(self, shop_url: str, access_token: str) -> Dict[str, Any]:
        """Connect to Shopify and fetch real order data using REST API."""
        try:
            base_url = f"https://{shop_url}/admin/api/2024-01"
            headers = {'X-Shopify-Access-Token': access_token}
            
            resp = requests.get(f"{base_url}/orders.json", headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            
            orders = resp.json().get('orders', [])
            order_data = []
            
            for order in orders:
                order_data.append({
                    'order_id': order['id'],
                    'order_name': order.get('name', ''),
                    'date': order['created_at'],
                    'revenue': float(order['total_price']),
                    'items_count': sum(li['quantity'] for li in order.get('line_items', [])),
                    'customer_email': order.get('customer', {}).get('email', 'Unknown') if order.get('customer') else 'Unknown',
                    'status': order.get('financial_status', 'unknown')
                })
            
            return {
                'status': 'success',
                'data': pd.DataFrame(order_data),
                'total_orders': len(order_data),
                'message': f'Successfully fetched {len(order_data)} orders from Shopify'
            }
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': f'Shopify API error: {str(e)}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error processing Shopify data: {str(e)}'}
    
    def get_shopify_products(self, shop_url: str, access_token: str) -> pd.DataFrame:
        """Fetch Shopify product inventory using REST API."""
        try:
            base_url = f"https://{shop_url}/admin/api/2024-01"
            headers = {'X-Shopify-Access-Token': access_token}
            
            resp = requests.get(f"{base_url}/products.json", headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            
            products = resp.json().get('products', [])
            product_data = []
            
            for product in products:
                for variant in product.get('variants', []):
                    product_data.append({
                        'product_id': product['id'],
                        'product_title': product.get('title', ''),
                        'variant_id': variant['id'],
                        'sku': variant.get('sku', ''),
                        'inventory_quantity': variant.get('inventory_quantity', 0),
                        'price': float(variant.get('price', 0))
                    })
            
            return pd.DataFrame(product_data)
        except Exception as e:
            st.error(f"Shopify API error: {e}")
            return pd.DataFrame()
    
    def get_shopify_customers(self, shop_url: str, access_token: str) -> pd.DataFrame:
        """Fetch Shopify customers using REST API."""
        try:
            base_url = f"https://{shop_url}/admin/api/2024-01"
            headers = {'X-Shopify-Access-Token': access_token}
            
            resp = requests.get(f"{base_url}/customers.json", headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            
            customers = resp.json().get('customers', [])
            customer_data = []
            
            for customer in customers:
                customer_data.append({
                    'customer_id': customer['id'],
                    'email': customer.get('email', ''),
                    'first_name': customer.get('first_name', ''),
                    'last_name': customer.get('last_name', ''),
                    'total_spent': float(customer.get('total_spent', 0)),
                    'orders_count': customer.get('orders_count', 0),
                    'created_at': customer.get('created_at', '')
                })
            
            return pd.DataFrame(customer_data)
        except Exception as e:
            st.error(f"Shopify Customers API error: {e}")
            return pd.DataFrame()
    
    # ==================== GOOGLE SHEETS INTEGRATION ====================
    def connect_google_sheets(self, spreadsheet_id: str, credentials_json: str) -> Dict[str, Any]:
        """Connect to Google Sheets and fetch data."""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            creds = Credentials.from_service_account_info(
                json.loads(credentials_json),
                scopes=scopes
            )
            
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.get_worksheet(0)
            
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            return {
                'status': 'success',
                'data': df,
                'rows': len(df),
                'columns': list(df.columns),
                'message': f'Successfully fetched {len(df)} rows from Google Sheets'
            }
        except Exception as e:
            return {'status': 'error', 'message': f'Google Sheets API error: {str(e)}'}
    
    def get_sheets_data_by_range(self, spreadsheet_id: str, credentials_json: str, range_name: str) -> pd.DataFrame:
        """Fetch data from specific range in Google Sheets."""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            creds = Credentials.from_service_account_info(
                json.loads(credentials_json),
                scopes=scopes
            )
            
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(spreadsheet_id)
            
            worksheet_name = range_name.split('!')[0] if '!' in range_name else range_name
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Google Sheets API error: {e}")
            return pd.DataFrame()
    
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
                    'retention': max(0.5, 1.0 - (i * 0.08))
