"""Phase 4: Model Training Infrastructure
Automated training, evaluation, and model versioning

This module handles:
- Training pipelines for Churn, Demand, and Anomaly models
- Hyperparameter tuning
- Model evaluation and cross-validation
- Model versioning and persistence
- Training metrics and logging
"""

import logging
from datetime import datetime
from typing import Dict, Tuple, List, Any
import json
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.model_selection import cross_val_score, GridSearchCV
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainingPipeline:
    """Automated model training and evaluation"""
    
    def __init__(self, model_name: str, model_type: str = 'classification'):
        """Initialize training pipeline
        
        Args:
            model_name: Name of the model
            model_type: 'classification' or 'regression'
        """
        self.model_name = model_name
        self.model_type = model_type
        self.model = None
        self.best_params = None
        self.metrics = {}
        self.training_history = []
        self.model_version = None
        self.trained_at = None
        
    def train_classification_model(self, X_train, y_train, model_type: str = 'random_forest'):
        """Train a classification model
        
        Args:
            X_train: Training features
            y_train: Training labels
            model_type: Type of classifier
        """
        logger.info(f"Training {model_type} classifier...")
        
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42
            )
        elif model_type == 'logistic_regression':
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.model.fit(X_train, y_train)
        self.trained_at = datetime.now().isoformat()
        logger.info(f"{model_type} classifier trained successfully")
        
        return self.model
    
    def train_regression_model(self, X_train, y_train, model_type: str = 'gradient_boosting'):
        """Train a regression model
        
        Args:
            X_train: Training features
            y_train: Training targets
            model_type: Type of regressor
        """
        logger.info(f"Training {model_type} regressor...")
        
        if model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.model.fit(X_train, y_train)
        self.trained_at = datetime.now().isoformat()
        logger.info(f"{model_type} regressor trained successfully")
        
        return self.model
    
    def evaluate_classification(self, X_test, y_test, y_pred_proba=None):
        """Evaluate classification model
        
        Args:
            X_test: Test features
            y_test: Test labels
            y_pred_proba: Predicted probabilities (for ROC-AUC)
            
        Returns:
            Dictionary with evaluation metrics
        """
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            'f1': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        }
        
        if y_pred_proba is not None:
            try:
                metrics['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba, multi_class='ovr'))
            except:
                metrics['roc_auc'] = None
        
        self.metrics = metrics
        logger.info(f"Classification metrics: {metrics}")
        return metrics
    
    def evaluate_regression(self, X_test, y_test):
        """Evaluate regression model
        
        Args:
            X_test: Test features
            y_test: Test targets
            
        Returns:
            Dictionary with evaluation metrics
        """
        y_pred = self.model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2)
        }
        
        self.metrics = metrics
        logger.info(f"Regression metrics: {metrics}")
        return metrics
    
    def cross_validate(self, X, y, cv: int = 5):
        """Perform k-fold cross-validation
        
        Args:
            X: Features
            y: Labels/targets
            cv: Number of folds
            
        Returns:
            Dictionary with cross-validation scores
        """
        if self.model_type == 'classification':
            scoring = 'f1_weighted'
        else:
            scoring = 'r2'
        
        scores = cross_val_score(self.model, X, y, cv=cv, scoring=scoring)
        
        cv_results = {
            'mean_score': float(scores.mean()),
            'std_score': float(scores.std()),
            'fold_scores': scores.tolist()
        }
        
        logger.info(f"Cross-validation scores: {scores.tolist()}")
        return cv_results
    
    def hyperparameter_tuning(self, X_train, y_train, param_grid: Dict, cv: int = 5):
        """Perform hyperparameter tuning with GridSearchCV
        
        Args:
            X_train: Training features
            y_train: Training labels
            param_grid: Parameter grid for GridSearch
            cv: Number of folds
            
        Returns:
            Dictionary with tuning results
        """
        logger.info(f"Starting hyperparameter tuning with grid: {param_grid}")
        
        if self.model_type == 'classification':
            scoring = 'f1_weighted'
        else:
            scoring = 'r2'
        
        grid_search = GridSearchCV(self.model, param_grid, cv=cv, scoring=scoring, n_jobs=-1)
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        
        tuning_results = {
            'best_params': self.best_params,
            'best_score': float(grid_search.best_score_),
            'cv_results': {
                'mean_test_score': grid_search.cv_results_['mean_test_score'].tolist(),
                'std_test_score': grid_search.cv_results_['std_test_score'].tolist()
            }
        }
        
        logger.info(f"Best parameters: {self.best_params}")
        logger.info(f"Best cross-validation score: {grid_search.best_score_}")
        return tuning_results
    
    def get_feature_importance(self):
        """Get feature importance from tree-based models
        
        Returns:
            Dictionary mapping features to importance scores
        """
        if not hasattr(self.model, 'feature_importances_'):
            logger.warning("Model does not have feature_importances_")
            return {}
        
        importances = self.model.feature_importances_
        return {f'feature_{i}': float(imp) for i, imp in enumerate(importances)}
    
    def save_model(self, filepath: str):
        """Save model to disk
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            logger.error("No model to save")
            return
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Generate model version hash
        with open(filepath, 'rb') as f:
            self.model_version = hashlib.md5(f.read()).hexdigest()[:8]
        
        logger.info(f"Model saved to {filepath} (version: {self.model_version})")
    
    def load_model(self, filepath: str):
        """Load model from disk
        
        Args:
            filepath: Path to model file
        """
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        
        logger.info(f"Model loaded from {filepath}")
    
    def get_model_metadata(self):
        """Get comprehensive model metadata
        
        Returns:
            Dictionary with model information
        """
        metadata = {
            'model_name': self.model_name,
            'model_type': self.model_type,
            'trained_at': self.trained_at,
            'model_version': self.model_version,
            'metrics': self.metrics,
            'best_params': self.best_params,
            'feature_importance': self.get_feature_importance()
        }
        return metadata
    
    def log_training_history(self, training_info: Dict):
        """Log training execution details
        
        Args:
            training_info: Dictionary with training details
        """
        training_record = {
            'timestamp': datetime.now().isoformat(),
            'model_version': self.model_version,
            **training_info
        }
        self.training_history.append(training_record)
        logger.info(f"Training logged: {training_record}")


class ChurnPredictor(ModelTrainingPipeline):
    """Churn prediction model"""
    
    def __init__(self):
        super().__init__('churn_predictor', 'classification')
    
    def prepare_churn_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for churn prediction"""
        df_features = df.copy()
        
        # RFM features
        if 'recency' not in df_features.columns and 'date' in df_features.columns:
            df_features['recency'] = (datetime.now() - pd.to_datetime(df_features['date'])).dt.days
        
        if 'revenue' in df_features.columns and 'orders' in df_features.columns:
            df_features['aov'] = df_features['revenue'] / (df_features['orders'] + 1)
        
        return df_features


class DemandForecaster(ModelTrainingPipeline):
    """Demand forecasting model"""
    
    def __init__(self):
        super().__init__('demand_forecaster', 'regression')
    
    def prepare_demand_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for demand forecasting"""
        df_features = df.copy()
        
        # Seasonality features
        if 'date' in df_features.columns:
            df_features['date'] = pd.to_datetime(df_features['date'])
            df_features['month'] = df_features['date'].dt.month
            df_features['quarter'] = df_features['date'].dt.quarter
            df_features['day_of_week'] = df_features['date'].dt.dayofweek
        
        return df_features


class AnomalyDetector(ModelTrainingPipeline):
    """Anomaly detection model"""
    
    def __init__(self):
        super().__init__('anomaly_detector', 'classification')


if __name__ == "__main__":
    logger.info("Phase 4: Model Training Infrastructure loaded")
    logger.info("Available models: ChurnPredictor, DemandForecaster, AnomalyDetector")
