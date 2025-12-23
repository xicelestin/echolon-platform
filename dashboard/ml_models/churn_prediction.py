import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class ChurnPredictor:
    """
    Customer Churn Prediction Model using ensemble methods.
    
    Predicts which customers are at risk of churning based on behavioral
    and transactional features. Uses a combination of Random Forest and
    Gradient Boosting for robust predictions.
    """
    
    def __init__(self, random_state: int = 42, use_gradient_boosting: bool = True):
        """
        Initialize churn prediction model.
        
        Args:
            random_state: Random seed for reproducibility
            use_gradient_boosting: Whether to use GB in ensemble (default: True)
        """
        self.random_state = random_state
        self.use_gradient_boosting = use_gradient_boosting
        
        # Models
        self.rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.gb_model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=7,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            subsample=0.8
        ) if use_gradient_boosting else None
        
        # Preprocessing
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Feature importance
        self.feature_importance = None
        
        # Model performance
        self.cv_scores = {}
        
    def _encode_categorical(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Encode categorical features.
        
        Args:
            X: Input features
            fit: Whether to fit encoders (during training)
            
        Returns:
            DataFrame with encoded categorical features
        """
        X_encoded = X.copy()
        
        categorical_cols = X.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if fit:
                le = LabelEncoder()
                X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
                self.label_encoders[col] = le
            else:
                le = self.label_encoders[col]
                X_encoded[col] = le.transform(X_encoded[col].astype(str))
        
        return X_encoded
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Train churn prediction models.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training labels (n_samples,) - 0: no churn, 1: churn
            
        Returns:
            Dictionary with training metrics
        """
        # Encode categorical features
        X_encoded = self._encode_categorical(X, fit=True)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_encoded)
        
        # Train Random Forest
        self.rf_model.fit(X_scaled, y)
        rf_cv_score = cross_val_score(
            self.rf_model, X_scaled, y,
            cv=5, scoring='roc_auc'
        ).mean()
        
        self.cv_scores['RandomForest'] = rf_cv_score
        
        # Train Gradient Boosting if enabled
        if self.gb_model:
            self.gb_model.fit(X_scaled, y)
            gb_cv_score = cross_val_score(
                self.gb_model, X_scaled, y,
                cv=5, scoring='roc_auc'
            ).mean()
            self.cv_scores['GradientBoosting'] = gb_cv_score
        
        # Calculate feature importance (average of models)
        importances = self.rf_model.feature_importances_
        if self.gb_model:
            importances = (importances + self.gb_model.feature_importances_) / 2
        
        self.feature_importance = pd.DataFrame({
            'feature': X_encoded.columns,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return {
            'rf_cv_auc': rf_cv_score,
            'gb_cv_auc': self.cv_scores.get('GradientBoosting', None),
            'ensemble_cv_auc': np.mean(list(self.cv_scores.values()))
        }
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict churn probability (0-1 scale).
        
        Args:
            X: Feature data (n_samples, n_features)
            
        Returns:
            Churn probability array (n_samples,) with values 0-1
        """
        X_encoded = self._encode_categorical(X, fit=False)
        X_scaled = self.scaler.transform(X_encoded)
        
        # Get predictions from Random Forest
        rf_proba = self.rf_model.predict_proba(X_scaled)[:, 1]
        
        # Ensemble with Gradient Boosting if available
        if self.gb_model:
            gb_proba = self.gb_model.predict_proba(X_scaled)[:, 1]
            return (rf_proba + gb_proba) / 2
        else:
            return rf_proba
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """
        Predict churn labels.
        
        Args:
            X: Feature data
            threshold: Probability threshold for churn prediction (default: 0.5)
            
        Returns:
            Binary predictions (0/1)
        """
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)
    
    def get_churn_scores(self, X: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
        """
        Get detailed churn scores for each customer.
        
        Args:
            X: Feature data
            threshold: Decision threshold
            
        Returns:
            DataFrame with churn probability and risk level
        """
        proba = self.predict_proba(X)
        predictions = self.predict(X, threshold)
        
        result = pd.DataFrame({
            'churn_probability': proba,
            'churn_prediction': predictions,
            'risk_level': pd.cut(
                proba,
                bins=[0, 0.3, 0.6, 1.0],
                labels=['Low', 'Medium', 'High']
            )
        })
        
        return result
    
    def get_feature_importance(self, top_k: int = 10) -> pd.DataFrame:
        """
        Get top K most important features.
        
        Args:
            top_k: Number of top features to return
            
        Returns:
            DataFrame with feature importance scores
        """
        if self.feature_importance is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        return self.feature_importance.head(top_k)
    
    def get_at_risk_customers(self, X: pd.DataFrame, 
                             threshold: float = 0.6) -> pd.DataFrame:
        """
        Identify customers at risk of churning.
        
        Args:
            X: Feature data with customer identifiers
            threshold: Risk threshold (default: 0.6)
            
        Returns:
            DataFrame with at-risk customers sorted by risk
        """
        scores = self.get_churn_scores(X, threshold=0.5)
        X_with_scores = X.copy()
        X_with_scores['churn_probability'] = scores['churn_probability']
        X_with_scores['risk_level'] = scores['risk_level']
        
        at_risk = X_with_scores[X_with_scores['churn_probability'] >= threshold]
        return at_risk.sort_values('churn_probability', ascending=False)
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Evaluate model on test set.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary with evaluation metrics
        """
        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)
        
        return {
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_proba),
            'true_positives': np.sum((y_pred == 1) & (y_test == 1)),
            'false_positives': np.sum((y_pred == 1) & (y_test == 0)),
            'false_negatives': np.sum((y_pred == 0) & (y_test == 1))
        }
