"""Custom Features Module - Phase 6
Create business-specific features for enhanced insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomFeatureEngineering:
    """Generate custom business features from raw data"""
    
    def __init__(self):
        self.features_created = {}
        self.feature_stats = {}
    
    def temporal_features(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Extract temporal features from date columns"""
        df[date_col] = pd.to_datetime(df[date_col])
        
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['quarter'] = df[date_col].dt.quarter
        df['day_of_week'] = df[date_col].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['day_of_month'] = df[date_col].dt.day
        df['week_of_year'] = df[date_col].dt.isocalendar().week
        
        self.features_created['temporal'] = [
            'year', 'month', 'quarter', 'day_of_week', 
            'is_weekend', 'day_of_month', 'week_of_year'
        ]
        logger.info(f"Created {len(self.features_created['temporal'])} temporal features")
        return df
    
    def aggregation_features(self, df: pd.DataFrame, group_col: str, 
                            agg_cols: List[str]) -> pd.DataFrame:
        """Create aggregation-based features"""
        agg_features = {}
        
        for agg_col in agg_cols:
            # Rolling statistics
            df[f'{agg_col}_rolling_mean_7'] = df[agg_col].rolling(7).mean()
            df[f'{agg_col}_rolling_std_7'] = df[agg_col].rolling(7).std()
            df[f'{agg_col}_cumsum'] = df[agg_col].cumsum()
            
            # Growth rate
            df[f'{agg_col}_pct_change'] = df[agg_col].pct_change()
            
            agg_features[agg_col] = [
                f'{agg_col}_rolling_mean_7',
                f'{agg_col}_rolling_std_7',
                f'{agg_col}_cumsum',
                f'{agg_col}_pct_change'
            ]
        
        self.features_created['aggregation'] = agg_features
        logger.info(f"Created aggregation features for {len(agg_cols)} columns")
        return df
    
    def interaction_features(self, df: pd.DataFrame, 
                            feature_pairs: List[Tuple[str, str]]) -> pd.DataFrame:
        """Create interaction features from feature pairs"""
        interaction_cols = []
        
        for feat1, feat2 in feature_pairs:
            if feat1 in df.columns and feat2 in df.columns:
                # Multiplication interaction
                df[f'{feat1}_x_{feat2}'] = df[feat1] * df[feat2]
                
                # Ratio interaction (with division by zero handling)
                df[f'{feat1}_div_{feat2}'] = df[feat1] / (df[feat2] + 1e-8)
                
                # Sum and difference
                df[f'{feat1}_plus_{feat2}'] = df[feat1] + df[feat2]
                df[f'{feat1}_minus_{feat2}'] = df[feat1] - df[feat2]
                
                interaction_cols.extend([
                    f'{feat1}_x_{feat2}',
                    f'{feat1}_div_{feat2}',
                    f'{feat1}_plus_{feat2}',
                    f'{feat1}_minus_{feat2}'
                ])
        
        self.features_created['interaction'] = interaction_cols
        logger.info(f"Created {len(interaction_cols)} interaction features")
        return df
    
    def categorical_features(self, df: pd.DataFrame, 
                            cat_cols: List[str]) -> pd.DataFrame:
        """Create features from categorical variables"""
        categorical_features = []
        
        for cat_col in cat_cols:
            if cat_col in df.columns:
                # Frequency encoding
                freq_map = df[cat_col].value_counts(normalize=True).to_dict()
                df[f'{cat_col}_freq'] = df[cat_col].map(freq_map)
                
                # Label encoding
                df[f'{cat_col}_label'] = pd.factorize(df[cat_col])[0]
                
                categorical_features.extend([
                    f'{cat_col}_freq',
                    f'{cat_col}_label'
                ])
        
        self.features_created['categorical'] = categorical_features
        logger.info(f"Created {len(categorical_features)} categorical features")
        return df
    
    def business_logic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create domain-specific business logic features"""
        business_features = []
        
        # Example: Customer value segmentation
        if 'revenue' in df.columns:
            df['revenue_percentile'] = df['revenue'].rank(pct=True)
            df['high_value'] = (df['revenue_percentile'] > 0.75).astype(int)
            business_features.extend(['revenue_percentile', 'high_value'])
        
        # Example: Engagement score
        engagement_cols = [col for col in df.columns if 'engagement' in col.lower()]
        if engagement_cols:
            df['engagement_score'] = df[engagement_cols].mean(axis=1)
            business_features.append('engagement_score')
        
        # Example: Churn risk indicators
        if 'last_purchase_days_ago' in df.columns:
            df['churn_risk'] = (df['last_purchase_days_ago'] > 90).astype(int)
            business_features.append('churn_risk')
        
        self.features_created['business_logic'] = business_features
        logger.info(f"Created {len(business_features)} business logic features")
        return df
    
    def polynomial_features(self, df: pd.DataFrame, 
                           poly_cols: List[str], degree: int = 2) -> pd.DataFrame:
        """Create polynomial features"""
        poly_features = []
        
        for col in poly_cols:
            if col in df.columns:
                for d in range(2, degree + 1):
                    df[f'{col}_poly_{d}'] = df[col] ** d
                    poly_features.append(f'{col}_poly_{d}')
        
        self.features_created['polynomial'] = poly_features
        logger.info(f"Created {len(poly_features)} polynomial features")
        return df
    
    def get_feature_summary(self) -> Dict:
        """Return summary of all created features"""
        summary = {
            'total_features': sum(len(v) if isinstance(v, list) else len(v.values()) 
                                 for v in self.features_created.values()),
            'feature_groups': list(self.features_created.keys()),
            'features_by_group': self.features_created
        }
        return summary
    
    def complete_feature_pipeline(self, df: pd.DataFrame, 
                                 date_col: str = None,
                                 agg_cols: List[str] = None,
                                 cat_cols: List[str] = None) -> pd.DataFrame:
        """Execute complete feature engineering pipeline"""
        logger.info("Starting feature engineering pipeline...")
        original_cols = len(df.columns)
        
        if date_col and date_col in df.columns:
            df = self.temporal_features(df, date_col)
        
        if agg_cols:
            df = self.aggregation_features(df, 'id', agg_cols)
        
        if cat_cols:
            df = self.categorical_features(df, cat_cols)
        
        df = self.business_logic_features(df)
        
        new_cols = len(df.columns) - original_cols
        logger.info(f"Feature pipeline complete: Added {new_cols} features")
        
        return df


if __name__ == "__main__":
    # Example usage
    # feature_engineer = CustomFeatureEngineering()
    # df = pd.read_csv('./data/business_data.csv')
    # df = feature_engineer.complete_feature_pipeline(
    #     df, 
    #     date_col='date',
    #     agg_cols=['revenue', 'customers'],
    #     cat_cols=['category', 'region']
    # )
    pass
