"""ML Fine-tuning Module - Phase 6
Train machine learning models on actual business data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import joblib
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelFineTuning:
    """Fine-tune ML models with business data"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        
    def load_business_data(self) -> pd.DataFrame:
        """Load and validate business data"""
        try:
            df = pd.read_csv(self.data_path)
            logger.info(f"Loaded {len(df)} records from {self.data_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def preprocess_data(self, df: pd.DataFrame):
        """Preprocess data for model training"""
        # Handle missing values
        df = df.fillna(df.mean(numeric_only=True))
        
        # Remove outliers using IQR
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df = df[(df[col] >= Q1 - 1.5*IQR) & (df[col] <= Q3 + 1.5*IQR)]
        
        logger.info(f"Data preprocessed: {len(df)} records after cleaning")
        return df
    
    def train_regression_model(self, X_train, y_train, X_test, y_test):
        """Train regression model for continuous predictions"""
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        self.models['regression'] = model
        self.performance_metrics['regression'] = {
            'mse': float(mse),
            'rmse': float(np.sqrt(mse)),
            'r2_score': float(r2)
        }
        
        logger.info(f"Regression Model - RMSE: {np.sqrt(mse):.4f}, R²: {r2:.4f}")
        return model
    
    def train_classification_model(self, X_train, y_train, X_test, y_test):
        """Train classification model for categorical predictions"""
        model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.models['classification'] = model
        self.performance_metrics['classification'] = {
            'accuracy': float(accuracy),
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        logger.info(f"Classification Model - Accuracy: {accuracy:.4f}")
        return model
    
    def get_feature_importance(self, model_type: str) -> dict:
        """Extract feature importance from trained models"""
        if model_type not in self.models:
            return {}
        
        model = self.models[model_type]
        importance = model.feature_importances_
        return {'importance': importance.tolist()}
    
    def save_models(self, model_dir: str = './ml_models'):
        """Save trained models and metrics"""
        import os
        os.makedirs(model_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            path = f"{model_dir}/{model_name}_model.pkl"
            joblib.dump(model, path)
            logger.info(f"Saved {model_name} model to {path}")
        
        metrics_path = f"{model_dir}/performance_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.performance_metrics, f, indent=2)
        logger.info(f"Saved performance metrics to {metrics_path}")
    
    def fine_tune_pipeline(self, df: pd.DataFrame, target_col: str):
        """Complete fine-tuning pipeline"""
        logger.info("Starting ML fine-tuning pipeline...")
        
        # Preprocess
        df = self.preprocess_data(df)
        
        # Prepare features and target
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['feature_scaler'] = scaler
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train models
        if y.dtype == 'object' or len(y.unique()) < 20:
            self.train_classification_model(X_train, y_train, X_test, y_test)
        else:
            self.train_regression_model(X_train, y_train, X_test, y_test)
        
        logger.info("Fine-tuning pipeline completed successfully")
        return self.performance_metrics


if __name__ == "__main__":
    # Example usage
    fine_tuner = MLModelFineTuning('./data/business_data.csv')
    # Uncomment to run:
    # df = fine_tuner.load_business_data()
    # metrics = fine_tuner.fine_tune_pipeline(df, 'target_column')
    # fine_tuner.save_models()
