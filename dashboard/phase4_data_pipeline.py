"""Phase 4: Automated Data Pipeline
Data Loading, Preprocessing, and Feature Engineering

This module handles:
- Connecting to multiple data sources (CSV, database, API)
- Data validation and cleaning
- Feature engineering
- Data splitting for training/testing
- Automatic data profiling
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Optional
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPipeline:
    """Automated data loading and preprocessing pipeline"""
    
    def __init__(self, config: Dict = None):
        """Initialize the data pipeline
        
        Args:
            config: Configuration dictionary for data sources
        """
        self.config = config or {}
        self.raw_data = None
        self.processed_data = None
        self.data_profile = {}
        self.feature_stats = {}
        
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load data from CSV file
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with loaded data
        """
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} rows from {filepath}")
            self.raw_data = df
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise
    
    def load_from_database(self, connection_string: str, query: str) -> pd.DataFrame:
        """Load data from database
        
        Args:
            connection_string: Database connection string
            query: SQL query to execute
            
        Returns:
            DataFrame with queried data
        """
        try:
            # Placeholder for database connection
            # In production, use sqlalchemy: create_engine(connection_string)
            logger.info(f"Querying database with: {query[:50]}...")
            # df = pd.read_sql(query, connection_string)
            return pd.DataFrame()  # Placeholder
        except Exception as e:
            logger.error(f"Error loading from database: {str(e)}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """Validate data quality
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': len(df[df.duplicated()]),
            'data_types': df.dtypes.astype(str).to_dict(),
            'numeric_stats': {},
            'categorical_stats': {}
        }
        
        # Calculate numeric statistics
        for col in df.select_dtypes(include=[np.number]).columns:
            validation_report['numeric_stats'][col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'missing': int(df[col].isnull().sum())
            }
        
        # Calculate categorical statistics
        for col in df.select_dtypes(include=['object']).columns:
            validation_report['categorical_stats'][col] = {
                'unique_values': df[col].nunique(),
                'top_value': str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None,
                'missing': int(df[col].isnull().sum())
            }
        
        logger.info(f"Data validation complete. Duplicates: {validation_report['duplicates']}")
        return validation_report
    
    def clean_data(self, df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """Clean data by handling missing values and outliers
        
        Args:
            df: DataFrame to clean
            strategy: Strategy for handling missing values ('mean', 'median', 'drop')
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Handle missing values
        if strategy == 'drop':
            df_clean = df_clean.dropna()
            logger.info(f"Dropped rows with missing values. Remaining: {len(df_clean)} rows")
        elif strategy in ['mean', 'median']:
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df_clean[col].isnull().sum() > 0:
                    fill_value = df_clean[col].mean() if strategy == 'mean' else df_clean[col].median()
                    df_clean[col].fillna(fill_value, inplace=True)
            
            # Fill categorical columns with mode
            categorical_cols = df_clean.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df_clean[col].isnull().sum() > 0:
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
        
        # Remove duplicates
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df_clean)} duplicate rows")
        
        self.processed_data = df_clean
        return df_clean
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create new features from existing data
        
        Args:
            df: DataFrame to feature engineer
            
        Returns:
            DataFrame with engineered features
        """
        df_features = df.copy()
        
        # Time-based features
        if 'date' in df_features.columns:
            df_features['date'] = pd.to_datetime(df_features['date'])
            df_features['day_of_week'] = df_features['date'].dt.dayofweek
            df_features['month'] = df_features['date'].dt.month
            df_features['quarter'] = df_features['date'].dt.quarter
            df_features['day_of_month'] = df_features['date'].dt.day
        
        # Interaction features
        if 'revenue' in df_features.columns and 'orders' in df_features.columns:
            df_features['revenue_per_order'] = df_features['revenue'] / (df_features['orders'] + 1)
        
        if 'revenue' in df_features.columns and 'customers' in df_features.columns:
            df_features['revenue_per_customer'] = df_features['revenue'] / (df_features['customers'] + 1)
        
        # Ratio features
        if 'profit' in df_features.columns and 'revenue' in df_features.columns:
            df_features['profit_ratio'] = df_features['profit'] / (df_features['revenue'] + 1)
        
        # Lag features
        numeric_cols = df_features.select_dtypes(include=[np.number]).columns
        for col in ['revenue', 'orders', 'customers']:
            if col in numeric_cols:
                df_features[f'{col}_lag1'] = df_features[col].shift(1)
                df_features[f'{col}_lag7'] = df_features[col].shift(7)
                df_features[f'{col}_rolling_mean'] = df_features[col].rolling(window=7).mean()
        
        logger.info(f"Engineered {len(df_features.columns) - len(df.columns)} new features")
        return df_features
    
    def scale_features(self, df: pd.DataFrame, scaler_type: str = 'standard') -> Tuple[pd.DataFrame, object]:
        """Scale numerical features
        
        Args:
            df: DataFrame to scale
            scaler_type: Type of scaler ('standard' or 'minmax')
            
        Returns:
            Tuple of (scaled DataFrame, scaler object)
        """
        df_scaled = df.copy()
        numeric_cols = df_scaled.select_dtypes(include=[np.number]).columns
        
        if scaler_type == 'standard':
            scaler = StandardScaler()
        else:
            scaler = MinMaxScaler()
        
        df_scaled[numeric_cols] = scaler.fit_transform(df_scaled[numeric_cols])
        logger.info(f"Scaled {len(numeric_cols)} numerical features using {scaler_type} scaler")
        
        return df_scaled, scaler
    
    def split_train_test(self, df: pd.DataFrame, test_size: float = 0.2, 
                        random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into training and testing sets
        
        Args:
            df: DataFrame to split
            test_size: Proportion of test set
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (train_df, test_df)
        """
        train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)
        logger.info(f"Split data: {len(train_df)} training, {len(test_df)} testing")
        return train_df, test_df
    
    def profile_data(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive data profile
        
        Args:
            df: DataFrame to profile
            
        Returns:
            Dictionary with data profile statistics
        """
        profile = {
            'timestamp': datetime.now().isoformat(),
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'column_info': {},
            'missing_data_pct': float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
        }
        
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'non_null': int(df[col].count()),
                'null_pct': float((df[col].isnull().sum() / len(df)) * 100)
            }
            
            if df[col].dtype in [np.int64, np.float64]:
                col_info.update({
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std())
                })
            elif df[col].dtype == 'object':
                col_info['unique'] = int(df[col].nunique())
                col_info['top'] = str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None
            
            profile['column_info'][col] = col_info
        
        self.data_profile = profile
        return profile
    
    def execute_pipeline(self, df: pd.DataFrame, clean: bool = True,
                        engineer: bool = True, scale: bool = False) -> pd.DataFrame:
        """Execute complete data pipeline
        
        Args:
            df: Input DataFrame
            clean: Whether to clean data
            engineer: Whether to engineer features
            scale: Whether to scale features
            
        Returns:
            Processed DataFrame
        """
        logger.info("Starting data pipeline execution...")
        
        # Validate
        validation = self.validate_data(df)
        logger.info(f"Data validation: {validation['total_rows']} rows, {validation['duplicates']} duplicates")
        
        result_df = df.copy()
        
        # Clean
        if clean:
            result_df = self.clean_data(result_df)
        
        # Engineer features
        if engineer:
            result_df = self.engineer_features(result_df)
        
        # Scale
        if scale:
            result_df, _ = self.scale_features(result_df)
        
        # Profile
        profile = self.profile_data(result_df)
        logger.info(f"Pipeline complete. Final shape: {result_df.shape}")
        
        self.processed_data = result_df
        return result_df


if __name__ == "__main__":
    # Example usage
    pipeline = DataPipeline()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=365),
        'revenue': np.random.normal(50000, 10000, 365),
        'orders': np.random.poisson(100, 365),
        'customers': np.random.poisson(50, 365),
        'profit': np.random.normal(20000, 5000, 365)
    })
    
    # Execute pipeline
    processed = pipeline.execute_pipeline(sample_data)
    print(f"\nProcessed data shape: {processed.shape}")
    print(f"\nData profile: {json.dumps(pipeline.data_profile, indent=2, default=str)}")
