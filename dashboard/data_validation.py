"""Data Validation Module for Echolon Dashboard
Provides comprehensive data validation, quality checks, and error handling.
"""

import pandas as pd
import streamlit as st
from typing import Tuple, Dict, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validates CSV data with color-coded feedback."""
    
    # Define required columns for validation
    REQUIRED_COLUMNS = ['date', 'value']
    OPTIONAL_COLUMNS = ['customer_id', 'category', 'region']
    
    # Max file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Max rows for processing
    MAX_ROWS = 100000
    
    def __init__(self, df: pd.DataFrame):
        """Initialize validator with dataframe."""
        self.df = df
        self.validation_results = {}
        self.detected_columns = []
        self.quality_score = 0
        self.warnings = []
        self.errors = []
    
    def validate(self) -> Tuple[bool, Dict]:
        """Run complete validation."""
        self._check_columns()
        self._check_data_types()
        self._check_missing_values()
        self._check_duplicates()
        self._check_date_format()
        self._calculate_quality_score()
        
        return len(self.errors) == 0, self.get_report()
    
    def _check_columns(self) -> None:
        """Check for required columns."""
        missing = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
        present = set(self.REQUIRED_COLUMNS) & set(self.df.columns)
        
        if missing:
            self.errors.append(f"Missing columns: {', '.join(missing)}")
            self.validation_results['columns'] = 'error'
        else:
            self.validation_results['columns'] = 'success'
        
        # Detect optional columns
        self.detected_columns = [col for col in self.OPTIONAL_COLUMNS if col in self.df.columns]
        self.detected_columns.extend(present)
    
    def _check_data_types(self) -> None:
        """Check data types."""
        try:
            if 'value' in self.df.columns:
                pd.to_numeric(self.df['value'], errors='raise')
                self.validation_results['data_types'] = 'success'
        except:
            self.errors.append("Column 'value' contains non-numeric data")
            self.validation_results['data_types'] = 'error'
    
    def _check_missing_values(self) -> None:
        """Check for missing values."""
        missing_count = self.df.isnull().sum().sum()
        missing_pct = (missing_count / (len(self.df) * len(self.df.columns))) * 100
        
        if missing_pct > 20:
            self.warnings.append(f"{missing_pct:.1f}% missing values")
            self.validation_results['missing'] = 'warning'
        elif missing_count > 0:
            self.validation_results['missing'] = 'warning'
        else:
            self.validation_results['missing'] = 'success'
    
    def _check_duplicates(self) -> None:
        """Check for duplicate rows."""
        dup_count = self.df.duplicated().sum()
        if dup_count > 0:
            pct = (dup_count / len(self.df)) * 100
            self.warnings.append(f"{dup_count} duplicate rows ({pct:.1f}%)")
            self.validation_results['duplicates'] = 'warning'
        else:
            self.validation_results['duplicates'] = 'success'
    
    def _check_date_format(self) -> None:
        """Check date format."""
        if 'date' in self.df.columns:
            try:
                pd.to_datetime(self.df['date'])
                self.validation_results['date_format'] = 'success'
            except:
                self.warnings.append("Date column format may be invalid")
                self.validation_results['date_format'] = 'warning'
    
    def _calculate_quality_score(self) -> None:
        """Calculate overall data quality score (0-100)."""
        score = 100
        score -= len(self.errors) * 20  # -20 per error
        score -= len(self.warnings) * 5  # -5 per warning
        self.quality_score = max(0, score)
    
    def get_report(self) -> Dict:
        """Get validation report."""
        return {
            'valid': len(self.errors) == 0,
            'quality_score': self.quality_score,
            'detected_columns': self.detected_columns,
            'errors': self.errors,
            'warnings': self.warnings,
            'row_count': len(self.df),
            'column_count': len(self.df.columns),
        }
    
    def render_validation_ui(self) -> None:
        """Render color-coded validation feedback."""
        col1, col2, col3 = st.columns(3)
        
        # Column detection
        with col1:
            status = self.validation_results.get('columns', 'unknown')
            icon = '✅' if status == 'success' else '❌' if status == 'error' else '⚠️'
            st.metric(f"{icon} Columns", len(self.detected_columns), 
                     help=f"Detected: {', '.join(self.detected_columns)}")
        
        # Quality score
        with col2:
            color_score = 'green' if self.quality_score >= 80 else 'orange' if self.quality_score >= 60 else 'red'
            st.metric(f"📊 Quality Score", f"{self.quality_score}%", help=color_score)
        
        # Row count
        with col3:
            st.metric("📈 Rows", f"{len(self.df):,}")
        
        # Show errors
        if self.errors:
            st.error("\n".join([f"❌ {e}" for e in self.errors]))
        
        # Show warnings
        if self.warnings:
            st.warning("\n".join([f"⚠️ {w}" for w in self.warnings]))
        
        # Show success
        if not self.errors and not self.warnings:
            st.success("✅ All validations passed!")


def validate_csv_file(uploaded_file) -> Tuple[pd.DataFrame, bool, Dict]:
    """Validate uploaded CSV file."""
    try:
        # Check file size
        if uploaded_file.size > DataValidator.MAX_FILE_SIZE:
            return None, False, {'error': 'File exceeds 10MB limit'}
        
        # Read CSV
        df = pd.read_csv(uploaded_file)
        
        # Check row count
        if len(df) > DataValidator.MAX_ROWS:
            return None, False, {'error': f'File exceeds {DataValidator.MAX_ROWS:,} row limit'}
        
        # Validate
        validator = DataValidator(df)
        is_valid, report = validator.validate()
        
        return df, is_valid, report
    
    except Exception as e:
        return None, False, {'error': str(e)}


def get_validation_feedback(report: Dict) -> str:
    """Generate user-friendly validation feedback."""
    if not report.get('errors'):
        return f"✅ Data validated successfully! {report.get('row_count', 0):,} rows ready."
    return f"❌ Validation failed: {'; '.join(report.get('errors', []))}"
