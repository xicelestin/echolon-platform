"""Data Normalization Module for Echolon AI Platform

Handles flexible data upload with automatic column detection, normalization,
and intelligent metric inference for any CSV structure.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import streamlit as st


class DataNormalizer:
    """Automatically detect and normalize uploaded data to standard format."""
    
    # Column name mapping patterns
    DATE_PATTERNS = ['date', 'time', 'timestamp', 'day', 'period', 'datetime']
    REVENUE_PATTERNS = ['revenue', 'sales', 'income', 'gross_sales', 'total_sales', 'amount']
    ORDERS_PATTERNS = ['orders', 'transactions', 'purchases', 'order_count', 'num_orders']
    CUSTOMERS_PATTERNS = ['customers', 'users', 'clients', 'customer_count', 'unique_customers']
    COST_PATTERNS = ['cost', 'cogs', 'expenses', 'spend', 'ad_spend']
    UNITS_PATTERNS = ['units', 'quantity', 'items_sold', 'products_sold']
    
    def __init__(self):
        self.detected_columns = {}
        self.errors = []
        self.warnings = []
        
    def normalize_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Main normalization function.
        
        Args:
            df: Raw uploaded dataframe
            
        Returns:
            Tuple of (normalized_df, metadata_dict)
        """
        df_normalized = df.copy()
        
        # Step 1: Detect column mappings
        self._detect_columns(df)
        
        # Step 2: Rename columns to standard names
        df_normalized = self._rename_columns(df_normalized)
        
        # Step 3: Parse and validate date column
        df_normalized = self._parse_dates(df_normalized)
        
        # Step 4: Clean numeric columns
        df_normalized = self._clean_numeric_columns(df_normalized)
        
        # Step 5: Infer missing metrics
        df_normalized = self._infer_metrics(df_normalized)
        
        # Step 6: Add derived columns
        df_normalized = self._add_derived_columns(df_normalized)
        
        # Step 7: Validate data quality
        quality_report = self._validate_quality(df_normalized)
        
        return df_normalized, quality_report
    
    def _detect_columns(self, df: pd.DataFrame) -> None:
        """Detect which columns correspond to standard metrics."""
        columns_lower = {col: col.lower().replace('_', '').replace(' ', '') 
                        for col in df.columns}
        
        # Detect date column
        for col, col_clean in columns_lower.items():
            if any(pattern in col_clean for pattern in self.DATE_PATTERNS):
                self.detected_columns['date'] = col
                break
        
        # Detect revenue column
        for col, col_clean in columns_lower.items():
            if any(pattern in col_clean for pattern in self.REVENUE_PATTERNS):
                self.detected_columns['revenue'] = col
                break
        
        # Detect orders column
        for col, col_clean in columns_lower.items():
            if any(pattern in col_clean for pattern in self.ORDERS_PATTERNS):
                self.detected_columns['orders'] = col
                break
        
        # Detect customers column
        for col, col_clean in columns_lower.items():
            if any(pattern in col_clean for pattern in self.CUSTOMERS_PATTERNS):
                self.detected_columns['customers'] = col
                break
        
        # Detect cost column
        for col, col_clean in columns_lower.items():
            if any(pattern in col_clean for pattern in self.COST_PATTERNS):
                self.detected_columns['cost'] = col
                break
        
        # Detect units column
        for col, col_clean in columns_lower.items():
            if any(pattern in col_clean for pattern in self.UNITS_PATTERNS):
                self.detected_columns['units'] = col
                break
    
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename detected columns to standard names."""
        rename_map = {}
        for standard_name, original_col in self.detected_columns.items():
            if original_col in df.columns:
                rename_map[original_col] = standard_name
        
        return df.rename(columns=rename_map)
    
    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse date column to datetime format."""
        if 'date' not in df.columns:
            self.errors.append("No date column detected. Please ensure your data has a date/time column.")
            return df
        
        try:
            df['date'] = pd.to_datetime(df['date'])
        except Exception as e:
            self.errors.append(f"Could not parse date column: {str(e)}")
        
        return df
    
    def _clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and convert numeric columns."""
        numeric_cols = ['revenue', 'orders', 'customers', 'cost', 'units']
        
        for col in numeric_cols:
            if col in df.columns:
                try:
                    # Remove currency symbols and commas
                    if df[col].dtype == 'object':
                        df[col] = df[col].str.replace('$', '').str.replace(',', '')
                    
                    # Convert to numeric
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Fill NaN with 0
                    df[col] = df[col].fillna(0)
                    
                except Exception as e:
                    self.warnings.append(f"Issue cleaning {col}: {str(e)}")
        
        return df
    
    def _infer_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Infer missing metrics from available data."""
        
        # Infer Average Order Value if revenue and orders exist
        if 'revenue' in df.columns and 'orders' in df.columns:
            df['aov'] = df['revenue'] / df['orders'].replace(0, 1)
        
        # Infer cost if not present (use 40% of revenue as default)
        if 'cost' not in df.columns and 'revenue' in df.columns:
            df['cost'] = df['revenue'] * 0.40
            self.warnings.append("Cost data not found. Using 40% of revenue as estimated cost.")
        
        # Calculate profit
        if 'revenue' in df.columns and 'cost' in df.columns:
            df['profit'] = df['revenue'] - df['cost']
            df['profit_margin'] = (df['profit'] / df['revenue'].replace(0, 1)) * 100
        
        # Infer customers if not present but orders exist
        if 'customers' not in df.columns and 'orders' in df.columns:
            # Assume 1 customer per order (conservative estimate)
            df['customers'] = df['orders']
            self.warnings.append("Customer data not found. Using orders as proxy for unique customers.")
        
        # Calculate ROAS if revenue and cost exist
        if 'revenue' in df.columns and 'cost' in df.columns:
            df['roas'] = df['revenue'] / df['cost'].replace(0, 1)
        
        return df
    
    def _add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add useful derived columns for analysis."""
        
        if 'date' in df.columns:
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['day_of_week'] = df['date'].dt.day_name()
            df['week_of_year'] = df['date'].dt.isocalendar().week
        
        return df
    
    def _validate_quality(self, df: pd.DataFrame) -> Dict:
        """Generate data quality report."""
        report = {
            'total_rows': len(df),
            'date_range': None,
            'detected_columns': list(self.detected_columns.keys()),
            'missing_data': {},
            'errors': self.errors,
            'warnings': self.warnings,
            'quality_score': 100
        }
        
        # Date range
        if 'date' in df.columns and len(df) > 0:
            report['date_range'] = {
                'start': df['date'].min(),
                'end': df['date'].max(),
                'days': (df['date'].max() - df['date'].min()).days
            }
        
        # Check for missing data
        for col in df.columns:
            missing_pct = (df[col].isna().sum() / len(df)) * 100
            if missing_pct > 0:
                report['missing_data'][col] = f"{missing_pct:.1f}%"
                report['quality_score'] -= missing_pct * 0.1
        
        # Penalize for errors
        report['quality_score'] -= len(self.errors) * 10
        report['quality_score'] = max(0, min(100, report['quality_score']))
        
        return report


@st.cache_data(ttl=3600)
def process_uploaded_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
    """Process uploaded CSV/Excel file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Tuple of (normalized_df, quality_report)
    """
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel file.")
            return None, None
        
        # Normalize data
        normalizer = DataNormalizer()
        df_normalized, quality_report = normalizer.normalize_data(df_raw)
        
        return df_normalized, quality_report
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None, None


def display_quality_report(report: Dict) -> None:
    """Display data quality report in Streamlit UI."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Rows", report['total_rows'])
    
    with col2:
        quality_color = "green" if report['quality_score'] >= 80 else "orange" if report['quality_score'] >= 60 else "red"
        st.metric("Data Quality", f"{report['quality_score']:.0f}/100")
    
    with col3:
        if report['date_range']:
            st.metric("Days of Data", report['date_range']['days'])
    
    # Show detected columns
    if report['detected_columns']:
        st.success(f"✅ Detected columns: {', '.join(report['detected_columns'])}")
    
    # Show warnings
    if report['warnings']:
        with st.expander("⚠️ Warnings", expanded=False):
            for warning in report['warnings']:
                st.warning(warning)
    
    # Show errors
    if report['errors']:
        with st.expander("❌ Errors", expanded=True):
            for error in report['errors']:
                st.error(error)
    
    # Show missing data
    if report['missing_data']:
        with st.expander("📊 Missing Data Analysis", expanded=False):
            for col, pct in report['missing_data'].items():
                st.write(f"- {col}: {pct} missing")
