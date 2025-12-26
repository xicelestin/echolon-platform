# -*- coding: utf-8 -*-
"""
Real API integrations for Echolon AI Data Sources.
Supports Google Sheets, Shopify, QuickBooks, and Stripe.
"""
import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import requests
from typing import Optional, Dict, Any
import json

# ==================== GOOGLE SHEETS INTEGRATION ====================

def fetch_google_sheets_data(credentials: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Fetch data from Google Sheets using the Google Sheets API.
    
    Args:
        credentials: Dict containing 'spreadsheet_id' and 'sheet_name'
        
    Returns:
        DataFrame with the sheet data or None if error
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Get credentials from Streamlit secrets
        if 'google_sheets_credentials' in st.secrets:
            creds_dict = dict(st.secrets['google_sheets_credentials'])
            
            # Define the scope
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            # Authenticate
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            
            # Open the spreadsheet
            spreadsheet_id = credentials.get('spreadsheet_id')
            sheet_name = credentials.get('sheet_name', 'Sheet1')
            
            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Get all values and convert to DataFrame
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Try to parse date column if it exists
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            return df
        else:
            st.warning("Google Sheets credentials not configured in secrets.")
            return None
            
    except ImportError:
        st.error("gspread library not installed. Run: pip install gspread google-auth")
        return None
    except Exception as e:
        st.error(f"Error fetching Google Sheets data: {str(e)}")
        return None

# ==================== SHOPIFY INTEGRATION ====================

def fetch_shopify_data(credentials: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Fetch sales data from Shopify using the Shopify Admin API.
    
    Args:
        credentials: Dict containing 'shop_url', 'access_token'
        
    Returns:
        DataFrame with Shopify order data or None if error
    """
    try:
        shop_url = credentials.get('shop_url')  # e.g., 'your-store.myshopify.com'
        access_token = credentials.get('access_token')
        
        if not shop_url or not access_token:
            # Try to get from Streamlit secrets
            if 'shopify' in st.secrets:
                shop_url = st.secrets['shopify'].get('shop_url')
                access_token = st.secrets['shopify'].get('access_token')
        
        if not shop_url or not access_token:
            st.warning("Shopify credentials not provided or configured in secrets.")
            return None
        
        # Shopify API endpoint
        api_version = '2024-01'
        base_url = f"https://{shop_url}/admin/api/{api_version}"
        
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
        
        # Fetch orders from last 12 months
        created_at_min = (datetime.now() - timedelta(days=365)).isoformat()
        
        orders_url = f"{base_url}/orders.json"
        params = {
            'status': 'any',
            'created_at_min': created_at_min,
            'limit': 250  # Max per request
        }
        
        all_orders = []
        
        # Fetch orders (with pagination)
        while True:
            response = requests.get(orders_url, headers=headers, params=params)
            
            if response.status_code != 200:
                st.error(f"Shopify API error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            orders = data.get('orders', [])
            
            if not orders:
                break
            
            all_orders.extend(orders)
            
            # Check for pagination
            link_header = response.headers.get('Link')
            if not link_header or 'rel="next"' not in link_header:
                break
            
            # Extract next page URL
            next_url = None
            for link in link_header.split(','):
                if 'rel="next"' in link:
                    next_url = link.split('<')[1].split('>')[0]
                    break
            
            if not next_url:
                break
            
            orders_url = next_url
            params = {}  # Next URL already has params
        
        # Convert to DataFrame
        if not all_orders:
            st.info("No orders found in Shopify.")
            return None
        
        # Process orders into analytics format
        processed_data = []
        for order in all_orders:
            processed_data.append({
                'date': pd.to_datetime(order['created_at']).date(),
                'order_id': order['id'],
                'revenue': float(order.get('total_price', 0)),
                'customer_id': order.get('customer', {}).get('id'),
                'items': len(order.get('line_items', [])),
                'status': order.get('financial_status')
            })
        
        df = pd.DataFrame(processed_data)
        
        # Aggregate by date
        daily_data = df.groupby('date').agg({
            'revenue': 'sum',
            'order_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        
        daily_data.columns = ['date', 'revenue', 'orders', 'customers']
        
        # Add derived metrics
        daily_data['avg_order_value'] = daily_data['revenue'] / daily_data['orders']
        
        return daily_data
        
    except Exception as e:
        st.error(f"Error fetching Shopify data: {str(e)}")
        return None

# ==================== STRIPE INTEGRATION ====================

def fetch_stripe_data(credentials: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Fetch payment data from Stripe using the Stripe API.
    
    Args:
        credentials: Dict containing 'api_key'
        
    Returns:
        DataFrame with Stripe transaction data or None if error
    """
    try:
        import stripe
        
        api_key = credentials.get('api_key')
        
        if not api_key:
            # Try to get from Streamlit secrets
            if 'stripe' in st.secrets:
                api_key = st.secrets['stripe'].get('api_key')
        
        if not api_key:
            st.warning("Stripe API key not provided or configured in secrets.")
            return None
        
        stripe.api_key = api_key
        
        # Fetch charges from last 12 months
        created_after = int((datetime.now() - timedelta(days=365)).timestamp())
        
        charges = stripe.Charge.list(
            limit=100,
            created={'gte': created_after}
        )
        
        # Process charges into analytics format
        processed_data = []
        
        for charge in charges.auto_paging_iter():
            if charge.status == 'succeeded':
                processed_data.append({
                    'date': datetime.fromtimestamp(charge.created).date(),
                    'transaction_id': charge.id,
                    'revenue': charge.amount / 100,  # Convert from cents
                    'customer_id': charge.customer,
                    'currency': charge.currency
                })
        
        if not processed_data:
            st.info("No charges found in Stripe.")
            return None
        
        df = pd.DataFrame(processed_data)
        
        # Aggregate by date
        daily_data = df.groupby('date').agg({
            'revenue': 'sum',
            'transaction_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        
        daily_data.columns = ['date', 'revenue', 'orders', 'customers']
        
        return daily_data
        
    except ImportError:
        st.error("Stripe library not installed. Run: pip install stripe")
        return None
    except Exception as e:
        st.error(f"Error fetching Stripe data: {str(e)}")
        return None

# ==================== QUICKBOOKS INTEGRATION ====================

def fetch_quickbooks_data(credentials: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Fetch financial data from QuickBooks using the QuickBooks Online API.
    
    Args:
        credentials: Dict containing 'company_id', 'access_token', 'refresh_token'
        
    Returns:
        DataFrame with QuickBooks financial data or None if error
    """
    try:
        company_id = credentials.get('company_id')
        access_token = credentials.get('access_token')
        
        if not company_id or not access_token:
            # Try to get from Streamlit secrets
            if 'quickbooks' in st.secrets:
                company_id = st.secrets['quickbooks'].get('company_id')
                access_token = st.secrets['quickbooks'].get('access_token')
        
        if not company_id or not access_token:
            st.warning("QuickBooks credentials not provided or configured in secrets.")
            return None
        
        # QuickBooks API base URL
        base_url = f"https://quickbooks.api.intuit.com/v3/company/{company_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Fetch invoices
        query = "SELECT * FROM Invoice WHERE TxnDate >= '2024-01-01' MAXRESULTS 1000"
        invoices_url = f"{base_url}/query?query={query}"
        
        response = requests.get(invoices_url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"QuickBooks API error: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        invoices = data.get('QueryResponse', {}).get('Invoice', [])
        
        if not invoices:
            st.info("No invoices found in QuickBooks.")
            return None
        
        # Process invoices into analytics format
        processed_data = []
        for invoice in invoices:
            processed_data.append({
                'date': pd.to_datetime(invoice.get('TxnDate')),
                'invoice_id': invoice.get('Id'),
                'revenue': float(invoice.get('TotalAmt', 0)),
                'customer_id': invoice.get('CustomerRef', {}).get('value'),
                'status': invoice.get('Balance', 0) == 0 and 'paid' or 'unpaid'
            })
        
        df = pd.DataFrame(processed_data)
        
        # Aggregate by date
        daily_data = df.groupby('date').agg({
            'revenue': 'sum',
            'invoice_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        
        daily_data.columns = ['date', 'revenue', 'orders', 'customers']
        
        return daily_data
        
    except Exception as e:
        st.error(f"Error fetching QuickBooks data: {str(e)}")
        return None

# ==================== MAIN API ROUTER ====================

def fetch_data_from_api(source_key: str, credentials: Dict[str, Any] = None) -> Optional[pd.DataFrame]:
    """
    Main router function to fetch data from different APIs.
    
    Args:
        source_key: The data source type ('google_sheets', 'shopify', 'stripe', 'quickbooks')
        credentials: Optional credentials dict
        
    Returns:
        DataFrame with fetched data or None if error
    """
    if credentials is None:
        credentials = {}
    
    if source_key == 'google_sheets':
        return fetch_google_sheets_data(credentials)
    elif source_key == 'shopify':
        return fetch_shopify_data(credentials)
    elif source_key == 'stripe':
        return fetch_stripe_data(credentials)
    elif source_key == 'quickbooks':
        return fetch_quickbooks_data(credentials)
    else:
        st.error(f"Unknown data source: {source_key}")
        return None
