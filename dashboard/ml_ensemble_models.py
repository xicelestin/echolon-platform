"""ML Ensemble Models Module - Phase 7
Combine multiple models using voting, stacking, and blending techniques
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import VotingClassifier, VotingRegressor, StackingClassifier, StackingRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from typing import List, Dict, Tuple
import logging
import joblib
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnsembleModelBuilder:
    """Build and optimize ensemble models"""
    
    def __init__(self, model_type: str = 'regression'):
        self.model_type = model_type
        self.ensemble_model = None
        self.base_models = {}
        self.performance_metrics = {}
    
    def voting_classifier_ensemble(self, estimators: List[Tuple[str, object]],
                                   voting: str = 'soft', weights: List[float] = None):
        """Create voting classifier ensemble"""
        if voting not in ['hard', 'soft']:
            raise ValueError("voting must be 'hard' or 'soft'")
        
        self.ensemble_model = VotingClassifier(
            estimators=estimators,
            voting=voting,
            weights=weights
        )
        
        for name, model in estimators:
            self.base_models[name] = model
        
        logger.info(f"Created voting classifier with {len(estimators)} base models")
        logger.info(f"Voting strategy: {voting}")
        if weights:
            logger.info(f"Weights: {weights}")
        
        return self.ensemble_model
    
    def voting_regressor_ensemble(self, estimators: List[Tuple[str, object]],
                                 weights: List[float] = None):
        """Create voting regressor ensemble"""
        self.ensemble_model = VotingRegressor(
            estimators=estimators,
            weights=weights
        )
        
        for name, model in estimators:
            self.base_models[name] = model
        
        logger.info(f"Created voting regressor with {len(estimators)} base models")
        if weights:
            logger.info(f"Weights: {weights}")
        
        return self.ensemble_model
    
    def stacking_classifier_ensemble(self, estimators: List[Tuple[str, object]],
                                    final_estimator: object,
                                    cv: int = 5):
        """Create stacking classifier ensemble"""
        self.ensemble_model = StackingClassifier(
            estimators=estimators,
            final_estimator=final_estimator,
            cv=cv
        )
        
        for name, model in estimators:
            self.base_models[name] = model
        
        logger.info(f"Created stacking classifier with {len(estimators)} base models")
        logger.info(f"Final estimator: {final_estimator.__class__.__name__}")
        logger.info(f"Cross-validation folds: {cv}")
        
        return self.ensemble_model
    
    def stacking_regressor_ensemble(self, estimators: List[Tuple[str, object]],
                                   final_estimator: object,
                                   cv: int = 5):
        """Create stacking regressor ensemble"""
        self.ensemble_model = StackingRegressor(
            estimators=estimators,
            final_estimator=final_estimator,
            cv=cv
        )
        
        for name, model in estimators:
            self.base_models[name] = model
        
        logger.info(f"Created stacking regressor with {len(estimators)} base models")
        logger.info(f"Final estimator: {final_estimator.__class__.__name__}")
        logger.info(f"Cross-validation folds: {cv}")
        
        return self.ensemble_model
    
    def fit_ensemble(self, X_train, y_train):
        """Train the ensemble model"""
        if self.ensemble_model is None:
            raise ValueError("No ensemble model created. Call voting/stacking method first.")
        
        logger.info("Training ensemble model...")
        self.ensemble_model.fit(X_train, y_train)
        logger.info("Ensemble model training completed.")
        
        return self.ensemble_model
    
    def predict(self, X_test):
        """Make predictions with ensemble model"""
        if self.ensemble_model is None:
            raise ValueError("Ensemble model not fitted.")
        
        return self.ensemble_model.predict(X_test)
    
    def predict_proba(self, X_test):
        """Get prediction probabilities (classification only)"""
        if self.model_type != 'classification':
            raise ValueError("predict_proba only available for classification.")
        
        return self.ensemble_model.predict_proba(X_test)
    
    def evaluate_ensemble(self, X_test, y_test):
        """Evaluate ensemble model performance"""
        predictions = self.predict(X_test)
        
        if self.model_type == 'classification':
            accuracy = accuracy_score(y_test, predictions)
            self.performance_metrics['accuracy'] = accuracy
            logger.info(f"Ensemble Accuracy: {accuracy:.4f}")
            return {'accuracy': accuracy}
        else:
            mse = mean_squared_error(y_test, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, predictions)
            
            self.performance_metrics['mse'] = mse
            self.performance_metrics['rmse'] = rmse
            self.performance_metrics['r2'] = r2
            
            logger.info(f"Ensemble MSE: {mse:.4f}")
            logger.info(f"Ensemble RMSE: {rmse:.4f}")
            logger.info(f"Ensemble R² Score: {r2:.4f}")
            
            return {'mse': mse, 'rmse': rmse, 'r2': r2}
    
    def get_base_model_predictions(self, X_test):
        """Get predictions from individual base models"""
        base_predictions = {}
        
        for name, model in self.base_models.items():
            base_predictions[name] = model.predict(X_test)
        
        return base_predictions
    
    def save_ensemble(self, filepath: str):
        """Save ensemble model to disk"""
        joblib.dump(self.ensemble_model, filepath)
        logger.info(f"Ensemble model saved to {filepath}")
    
    def load_ensemble(self, filepath: str):
        """Load ensemble model from disk"""
        self.ensemble_model = joblib.load(filepath)
        logger.info(f"Ensemble model loaded from {filepath}")
    
    def get_ensemble_summary(self) -> Dict:
        """Get summary of ensemble configuration"""
        return {
            'model_type': self.model_type,
            'ensemble_type': self.ensemble_model.__class__.__name__ if self.ensemble_model else None,
            'num_base_models': len(self.base_models),
            'base_models': list(self.base_models.keys()),
            'performance_metrics': self.performance_metrics,
            'timestamp': datetime.now().isoformat()
        }


class BlendingEnsemble:
    """Blending ensemble method for model combination"""
    
    def __init__(self):
        self.base_models = []
        self.meta_model = None
        self.blend_predictions = None
    
    def fit(self, X_train, X_blend, y_train, y_blend, base_models: List, meta_model):
        """Train blending ensemble
        
        Args:
            X_train, y_train: Training data
            X_blend, y_blend: Blending/validation data
            base_models: List of base models
            meta_model: Meta-learner model
        """
        self.base_models = base_models
        self.meta_model = meta_model
        
        # Train base models and generate blend predictions
        blend_predictions = np.zeros((X_blend.shape[0], len(base_models)))
        
        for i, model in enumerate(base_models):
            logger.info(f"Training base model {i+1}/{len(base_models)}...")
            model.fit(X_train, y_train)
            blend_predictions[:, i] = model.predict(X_blend)
        
        # Train meta-model on blend predictions
        logger.info("Training meta-model...")
        self.meta_model.fit(blend_predictions, y_blend)
        self.blend_predictions = blend_predictions
        
        logger.info("Blending ensemble training completed.")
    
    def predict(self, X_test):
        """Make predictions with blending ensemble"""
        if not self.base_models or self.meta_model is None:
            raise ValueError("Blending ensemble not fitted.")
        
        # Generate base model predictions
        test_predictions = np.zeros((X_test.shape[0], len(self.base_models)))
        
        for i, model in enumerate(self.base_models):
            test_predictions[:, i] = model.predict(X_test)
        
        # Get meta-model predictions
        final_predictions = self.meta_model.predict(test_predictions)
        return final_predictions
    
    def evaluate(self, X_test, y_test, task_type: str = 'regression'):
        """Evaluate blending ensemble"""
        predictions = self.predict(X_test)
        
        if task_type == 'classification':
            score = accuracy_score(y_test, predictions)
            logger.info(f"Blending Ensemble Accuracy: {score:.4f}")
            return {'accuracy': score}
        else:
            mse = mean_squared_error(y_test, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, predictions)
            
            logger.info(f"Blending Ensemble MSE: {mse:.4f}")
            logger.info(f"Blending Ensemble RMSE: {rmse:.4f}")
            logger.info(f"Blending Ensemble R² Score: {r2:.4f}")
            
            return {'mse': mse, 'rmse': rmse, 'r2': r2}


class EnsembleWeightOptimizer:
    """Optimize ensemble member weights"""
    
    @staticmethod
    def optimize_weights(base_predictions: List[np.ndarray], y_true: np.ndarray,
                        task_type: str = 'regression'):
        """Optimize weights for ensemble members
        
        Args:
            base_predictions: List of predictions from base models
            y_true: True labels/values
            task_type: 'regression' or 'classification'
        """
        from scipy.optimize import minimize
        
        n_models = len(base_predictions)
        
        def objective(weights):
            weighted_pred = np.average(np.array(base_predictions), axis=0, weights=weights)
            
            if task_type == 'regression':
                return mean_squared_error(y_true, weighted_pred)
            else:
                predictions = (weighted_pred > 0.5).astype(int)
                return 1 - accuracy_score(y_true, predictions)
        
        # Constraint: weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},)
        bounds = [(0, 1)] * n_models
        
        # Initial guess: equal weights
        x0 = np.ones(n_models) / n_models
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        optimal_weights = result.x
        logger.info(f"Optimal ensemble weights: {optimal_weights}")
        
        return optimal_weights


if __name__ == "__main__":
    # Example usage
    # from ml_hyperparameter_tuning import HyperparameterTuner
    # builder = EnsembleModelBuilder(model_type='regression')
    # estimators = [
    #     ('rf', RandomForestRegressor(n_estimators=100)),
    #     ('gb', GradientBoostingRegressor(n_estimators=100)),
    #     ('svr', SVR(kernel='rbf'))
    # ]
    # ensemble = builder.voting_regressor_ensemble(estimators, weights=[0.4, 0.4, 0.2])
    # ensemble = builder.fit_ensemble(X_train, y_train)
    # metrics = builder.evaluate_ensemble(X_test, y_test)
    pass
