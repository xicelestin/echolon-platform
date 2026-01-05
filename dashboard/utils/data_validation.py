# -*- coding: utf-8 -*-
"""
Data Validation Utilities for Echolon AI Dashboard

Provides comprehensive data validation, error handling, and safe data access
functions to prevent runtime errors and improve user experience.

Author: Echolon AI Team
Date: January 5, 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Comprehensive data validation class for dashboard operations.
    
    Provides methods for:
    - Column existence validation
    - Data type validation  
    - Value range validation
    - Missing data detection
    - Safe data access with fallbacks
    """
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame, 
                                 required_columns: List[str],
                                 show_ui: bool = True) -> bool:
        """
        Validate that dataframe contains all required columns.
        
        Args:
            df: DataFrame to validate
            required_columns: List of column names that must be present
            show_ui: Whether to show Streamlit UI messages
            
        Returns:
            bool: True if all required columns exist, False otherwise
        """
        if df is None or df.empty:
            if show_ui:
                st.error("❌ No data available. Please upload data or use demo data.")
            logger.error("DataFrame is None or empty")
            return False
        
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            if show_ui:
                st.error(f"❌ Missing required columns: {', '.join(missing)}")
                st.info(f"💡 Your data should include: {', '.join(required_columns)}")
                
                with st.expander("🔍 Available Columns"):
                    st.write(list(df.columns))
            
            logger.warning(f"Missing columns: {missing}")
            return False
        
        logger.info(f"All required columns present: {required_columns}")
        return True
    
    @staticmethod
    def safe_get_column(df: pd.DataFrame, 
                       column: str, 
                       default: Any = 0,
                       show_warning: bool = True) -> pd.Series:
        """
        Safely get column from dataframe with fallback default.
        
        Args:
            df: DataFrame to get column from
            column: Column name to retrieve
            default: Default value if column doesn't exist
            show_warning: Whether to show warning if column missing
            
        Returns:
            pd.Series: Column data or Series filled with default value
        """
        if df is None or df.empty:
            logger.warning(f"DataFrame is empty, returning empty series for '{column}'")
            return pd.Series([], dtype=float)
        
        if column in df.columns:
            return df[column]
        else:
            if show_warning:
                st.warning(f"⚠️ Column '{column}' not found. Using default value: {default}")
            logger.warning(f"Column '{column}' not found, using default: {default}")
            return pd.Series([default] * len(df))
    
    @staticmethod
    def validate_numeric_column(df: pd.DataFrame, 
                               column: str,
                               min_value: Optional[float] = None,
                               max_value: Optional[float] = None) -> bool:
        """
        Validate that column contains numeric data within specified range.
        
        Args:
            df: DataFrame containing the column
            column: Column name to validate
            min_value: Optional minimum allowed value
            max_value: Optional maximum allowed value
            
        Returns:
            bool: True if validation passes
        """
        if column not in df.columns:
            st.error(f"❌ Column '{column}' does not exist")
            return False
        
        # Check if numeric
        if not pd.api.types.is_numeric_dtype(df[column]):
            st.error(f"❌ Column '{column}' must contain numeric data")
            return False
        
        # Check range if specified
        if min_value is not None:
            if df[column].min() < min_value:
                st.warning(f"⚠️ Column '{column}' contains values below minimum: {min_value}")
                return False
        
        if max_value is not None:
            if df[column].max() > max_value:
                st.warning(f"⚠️ Column '{column}' contains values above maximum: {max_value}")
                return False
        
        return True
    
    @staticmethod
    def check_missing_data(df: pd.DataFrame, 
                          column: str,
                          threshold: float = 0.1) -> Dict[str, Any]:
        """
        Check for missing data in a column and provide statistics.
        
        Args:
            df: DataFrame to check
            column: Column name to analyze
            threshold: Maximum acceptable missing data percentage (0-1)
            
        Returns:
            dict: Statistics about missing data
        """
        if column not in df.columns:
            return {'error': f"Column '{column}' not found"}
        
        total_rows = len(df)
        missing_count = df[column].isna().sum()
        missing_pct = missing_count / total_rows if total_rows > 0 else 0
        
        result = {
            'column': column,
            'total_rows': total_rows,
            'missing_count': missing_count,
            'missing_percentage': missing_pct,
            'has_issue': missing_pct > threshold
        }
        
        if result['has_issue']:
            st.warning(
                f"⚠️ Column '{column}' has {missing_pct:.1%} missing data "
                f"({missing_count}/{total_rows} rows)"
            )
        
        return result
    
    @staticmethod
    def validate_date_column(df: pd.DataFrame, column: str) -> bool:
        """
        Validate that column contains valid date/datetime data.
        
        Args:
            df: DataFrame containing the column
            column: Column name to validate
            
        Returns:
            bool: True if valid date column
        """
        if column not in df.columns:
            st.error(f"❌ Column '{column}' does not exist")
            return False
        
        # Try to convert to datetime
        try:
            pd.to_datetime(df[column])
            return True
        except Exception as e:
            st.error(f"❌ Column '{column}' does not contain valid dates: {str(e)}")
            logger.error(f"Date validation failed for '{column}': {str(e)}")
            return False
    
    @staticmethod
    def get_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            dict: Complete data quality metrics
        """
        if df is None or df.empty:
            return {'error': 'DataFrame is empty'}
        
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_data': {},
            'duplicates': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024*1024)
        }
        
        # Check missing data for each column
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                report['missing_data'][col] = {
                    'count': int(missing),
                    'percentage': float(missing / len(df))
                }
        
        return report


def validate_dashboard_data(df: pd.DataFrame, 
                           data_type: str = 'general') -> bool:
    """
    Validate data for specific dashboard use cases.
    
    Args:
        df: DataFrame to validate
        data_type: Type of dashboard data ('general', 'sales', 'inventory', 'customers')
        
    Returns:
        bool: True if data is valid for the specified use case
    """
    validator = DataValidator()
    
    # Define required columns for each data type
    required_columns = {
        'general': ['date', 'revenue'],
        'sales': ['date', 'revenue', 'orders'],
        'inventory': ['date', 'inventory_units'],
        'customers': ['date', 'customers']
    }
    
    required = required_columns.get(data_type, required_columns['general'])
    
    if not validator.validate_required_columns(df, required):
        return False
    
    # Validate date column
    if not validator.validate_date_column(df, 'date'):
        return False
    
    # Validate numeric columns
    numeric_cols = [col for col in required if col != 'date']
    for col in numeric_cols:
        if not validator.validate_numeric_column(df, col, min_value=0):
            st.warning(f"⚠️ Negative values found in '{col}' column")
    
    st.success("✅ Data validation passed!")
    logger.info(f"Data validation passed for type: {data_type}")
    return True


@st.cache_data(ttl=3600)
def get_validated_data(df: pd.DataFrame, 
                      required_columns: List[str]) -> Optional[pd.DataFrame]:
    """
    Get validated and cleaned dataframe with caching.
    
    Args:
        df: Input DataFrame
        required_columns: Columns that must be present
        
    Returns:
        pd.DataFrame: Validated and cleaned dataframe, or None if validation fails
    """
    validator = DataValidator()
    
    if not validator.validate_required_columns(df, required_columns, show_ui=False):
        return None
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Clean numeric columns
    for col in required_columns:
        if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
            # Replace infinities with NaN
            df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
            # Fill NaN with 0 for numeric columns
            df_clean[col] = df_clean[col].fillna(0)
    
    logger.info(f"Data cleaned and validated: {len(df_clean)} rows")
    return df_clean


def safe_divide(numerator: Union[float, pd.Series], 
               denominator: Union[float, pd.Series],
               default: float = 0) -> Union[float, pd.Series]:
    """
    Safely divide two values, handling division by zero.
    
    Args:
        numerator: Value or Series to divide
        denominator: Value or Series to divide by
        default: Default value when division by zero occurs
        
    Returns:
        Result of division or default value
    """
    try:
        with np.errstate(divide='ignore', invalid='ignore'):
            result = numerator / denominator
            if isinstance(result, pd.Series):
                result = result.replace([np.inf, -np.inf], default).fillna(default)
            elif not np.isfinite(result):
                result = default
        return result
    except Exception as e:
        logger.warning(f"Division error: {str(e)}")
        return default


if __name__ == "__main__":
    # Example usage and testing
    print("Data Validation Utilities loaded successfully")
    
    # Create test data
    test_df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'revenue': [100, 200, 150, np.nan, 300, 250, 400, 350, 500, 450],
        'orders': [5, 10, 8, 6, 15, 12, 20, 18, 25, 22]
    })
    
    # Test validator
    validator = DataValidator()
    report = validator.get_data_quality_report(test_df)
    print("\nData Quality Report:")
    print(f"Total Rows: {report['total_rows']}")
    print(f"Total Columns: {report['total_columns']}")
    print(f"Missing Data: {report['missing_data']}")
