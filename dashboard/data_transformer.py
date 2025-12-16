"""Data Transformation Pipeline for Echolon Dashboard
Provides data cleaning, normalization, and transformation capabilities.
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Callable, List, Tuple, Dict
from datetime import datetime


class DataTransformer:
    """Handles data transformation and cleaning operations."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize transformer with dataframe."""
        self.df = df.copy()
        self.original_df = df.copy()
        self.transformations_applied = []
    
    def remove_duplicates(self, subset: List[str] = None, keep: str = 'first') -> 'DataTransformer':
        """Remove duplicate rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        after = len(self.df)
        self.transformations_applied.append(f"Removed {before - after} duplicates")
        return self
    
    def normalize_numeric(self, columns: List[str] = None) -> 'DataTransformer':
        """Normalize numeric columns to 0-1 range (min-max scaling)."""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        for col in columns:
            if col in self.df.columns:
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                if max_val - min_val != 0:
                    self.df[col] = (self.df[col] - min_val) / (max_val - min_val)
        
        self.transformations_applied.append(f"Normalized {len(columns)} numeric columns")
        return self
    
    def handle_missing_values(self, method: str = 'mean', columns: List[str] = None) -> 'DataTransformer':
        """Handle missing values using specified method.
        Methods: 'mean', 'median', 'forward_fill', 'drop'
        """
        if columns is None:
            columns = self.df.columns
        
        missing_count = self.df[columns].isnull().sum().sum()
        
        if missing_count > 0:
            if method == 'mean':
                for col in columns:
                    if self.df[col].dtype in [np.float64, np.int64]:
                        self.df[col].fillna(self.df[col].mean(), inplace=True)
            elif method == 'median':
                for col in columns:
                    if self.df[col].dtype in [np.float64, np.int64]:
                        self.df[col].fillna(self.df[col].median(), inplace=True)
            elif method == 'forward_fill':
                self.df[columns].fillna(method='ffill', inplace=True)
            elif method == 'drop':
                self.df = self.df.dropna(subset=columns)
            
            self.transformations_applied.append(f"Handled {missing_count} missing values using {method}")
        
        return self
    
    def parse_dates(self, date_columns: List[str], formats: List[str] = None) -> 'DataTransformer':
        """Parse date columns with flexible format detection.
        Formats: 'auto', 'YYYY-MM-DD', 'MM/DD/YYYY', 'DD-MM-YYYY'
        """
        format_map = {
            'auto': None,
            'YYYY-MM-DD': '%Y-%m-%d',
            'MM/DD/YYYY': '%m/%d/%Y',
            'DD-MM-YYYY': '%d-%m-%Y',
        }
        
        for i, col in enumerate(date_columns):
            if col in self.df.columns:
                fmt = format_map.get(formats[i] if formats and i < len(formats) else 'auto')
                try:
                    self.df[col] = pd.to_datetime(self.df[col], format=fmt, errors='coerce')
                    self.transformations_applied.append(f"Parsed {col} as datetime")
                except:
                    st.warning(f"Could not parse {col} as datetime")
        
        return self
    
    def remove_outliers(self, columns: List[str] = None, method: str = 'iqr', threshold: float = 1.5) -> 'DataTransformer':
        """Remove outliers using IQR or standard deviation method.
        Methods: 'iqr' (Interquartile Range), 'std' (Standard Deviation)
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        before = len(self.df)
        
        for col in columns:
            if col in self.df.columns:
                if method == 'iqr':
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    self.df = self.df[(self.df[col] >= lower_bound) & (self.df[col] <= upper_bound)]
                elif method == 'std':
                    mean = self.df[col].mean()
                    std = self.df[col].std()
                    self.df = self.df[np.abs(self.df[col] - mean) <= threshold * std]
        
        after = len(self.df)
        self.transformations_applied.append(f"Removed {before - after} outliers using {method}")
        return self
    
    def standardize_columns(self, columns: List[str] = None) -> 'DataTransformer':
        """Standardize column names (lowercase, replace spaces with underscores)."""
        if columns is None:
            columns = self.df.columns
        
        rename_map = {col: col.lower().replace(' ', '_').replace('-', '_') for col in columns}
        self.df.rename(columns=rename_map, inplace=True)
        self.transformations_applied.append("Standardized column names")
        return self
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get transformed dataframe."""
        return self.df
    
    def get_transformations(self) -> List[str]:
        """Get list of applied transformations."""
        return self.transformations_applied
    
    def render_transformation_ui(self) -> pd.DataFrame:
        """Render interactive data transformation UI."""
        st.subheader("🔄 Data Transformation Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Available Transformations:**")
            
            if st.checkbox("✅ Remove Duplicates", key='remove_dups_transform'):
                self.remove_duplicates()
                st.success(f"✅ Duplicates removed")
            
            if st.checkbox("📊 Normalize Numeric Values", key='normalize_numeric_transform'):
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
                self.normalize_numeric(numeric_cols)
                st.success(f"✅ Normalized {len(numeric_cols)} columns")
            
            if st.checkbox("📅 Parse Dates", key='parse_dates_transform'):
                date_cols = st.multiselect("Select date columns", self.df.columns)
                if date_cols:
                    self.parse_dates(date_cols)
                    st.success(f"✅ Parsed {len(date_cols)} date columns")
        
        with col2:
            st.write("**Advanced Options:**")
            
            if st.checkbox("⚔️ Remove Outliers", key='remove_outliers_transform'):
                method = st.radio("Outlier detection method:", ['iqr', 'std'])
                threshold = st.slider("Threshold:", 1.0, 3.0, 1.5)
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
                self.remove_outliers(numeric_cols, method, threshold)
                st.success(f"✅ Outliers removed using {method}")
            
            if st.checkbox("🏷️ Handle Missing Values", key='handle_missing_transform'):
                method = st.selectbox("Fill method:", ['mean', 'median', 'forward_fill', 'drop'])
                self.handle_missing_values(method)
                st.success(f"✅ Missing values handled with {method}")
        
        # Display applied transformations
        if self.transformations_applied:
            st.write("**Applied Transformations:**")
            for trans in self.transformations_applied:
                st.caption(f"✓ {trans}")
        
        return self.get_dataframe()


def get_transformation_options(df: pd.DataFrame) -> Dict:
    """Return available transformation options based on dataframe."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    return {
        'numeric_columns': numeric_cols,
        'date_columns': date_cols,
        'object_columns': object_cols,
        'has_missing': df.isnull().any().any(),
        'has_duplicates': df.duplicated().any(),
    }
