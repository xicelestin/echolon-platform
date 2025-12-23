"""ML Hyperparameter Tuning Module - Phase 7
Optimize model hyperparameters using GridSearch and Bayesian optimization
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier, RandomForestClassifier
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor
from typing import Dict, Tuple, List, Any
import logging
import json
from datetime import datetime

try:
    from skopt import gp_minimize, space
    BAYESIAN_AVAILABLE = True
except ImportError:
    BAYESIAN_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HyperparameterTuner:
    """Tune ML models using Grid Search and Bayesian optimization"""
    
    def __init__(self, model_type: str = 'regression', n_jobs: int = -1):
        self.model_type = model_type
        self.n_jobs = n_jobs
        self.best_model = None
        self.best_params = {}
        self.best_score = None
        self.cv_results = {}
        self.optimization_history = []
    
    def grid_search_regression(self, X_train, y_train, X_test=None, y_test=None):
        """Grid search for regression models"""
        model = RandomForestRegressor(random_state=42, n_jobs=self.n_jobs)
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'learning_rate': [0.01, 0.1, 0.5],
            'max_features': ['sqrt', 'log2']
        }
        
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring='r2',
            n_jobs=self.n_jobs, verbose=1
        )
        
        logger.info("Starting grid search for regression...")
        grid_search.fit(X_train, y_train)
        
        self.best_model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        self.best_score = grid_search.best_score_
        self.cv_results = grid_search.cv_results_
        
        logger.info(f"Best R² Score: {self.best_score:.4f}")
        logger.info(f"Best Parameters: {self.best_params}")
        
        return self.best_model
    
    def grid_search_classification(self, X_train, y_train, X_test=None, y_test=None):
        """Grid search for classification models"""
        model = GradientBoostingClassifier(random_state=42)
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'subsample': [0.8, 0.9, 1.0]
        }
        
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring='accuracy',
            n_jobs=self.n_jobs, verbose=1
        )
        
        logger.info("Starting grid search for classification...")
        grid_search.fit(X_train, y_train)
        
        self.best_model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        self.best_score = grid_search.best_score_
        self.cv_results = grid_search.cv_results_
        
        logger.info(f"Best Accuracy Score: {self.best_score:.4f}")
        logger.info(f"Best Parameters: {self.best_params}")
        
        return self.best_model
    
    def randomized_search(self, X_train, y_train, model, param_dist: Dict,
                         n_iter: int = 20, cv: int = 5):
        """Randomized search for faster exploration"""
        random_search = RandomizedSearchCV(
            model, param_distributions=param_dist,
            n_iter=n_iter, cv=cv, scoring='r2' if self.model_type == 'regression' else 'accuracy',
            n_jobs=self.n_jobs, random_state=42, verbose=1
        )
        
        logger.info(f"Starting randomized search with {n_iter} iterations...")
        random_search.fit(X_train, y_train)
        
        self.best_model = random_search.best_estimator_
        self.best_params = random_search.best_params_
        self.best_score = random_search.best_score_
        
        logger.info(f"Best Score: {self.best_score:.4f}")
        logger.info(f"Best Parameters: {self.best_params}")
        
        return self.best_model
    
    def bayesian_optimization(self, X_train, y_train, model, param_space: Dict,
                             n_calls: int = 20):
        """Bayesian optimization for efficient hyperparameter search"""
        if not BAYESIAN_AVAILABLE:
            logger.warning("scikit-optimize not installed. Falling back to random search.")
            return None
        
        def objective(params):
            model.set_params(**params)
            scores = cross_val_score(model, X_train, y_train, cv=3,
                                   scoring='r2' if self.model_type == 'regression' else 'accuracy')
            return -scores.mean()
        
        logger.info(f"Starting Bayesian optimization with {n_calls} calls...")
        result = gp_minimize(objective, list(param_space.values()),
                            n_calls=n_calls, random_state=42, verbose=1)
        
        self.best_params = dict(zip(param_space.keys(), result.x))
        self.best_score = -result.fun
        
        logger.info(f"Best Score: {self.best_score:.4f}")
        logger.info(f"Best Parameters: {self.best_params}")
        
        return self.best_params
    
    def cross_validation_analysis(self, model, X_train, y_train, cv: int = 5):
        """Analyze cross-validation performance"""
        scoring = 'r2' if self.model_type == 'regression' else 'accuracy'
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=scoring)
        
        cv_analysis = {
            'mean_score': cv_scores.mean(),
            'std_score': cv_scores.std(),
            'min_score': cv_scores.min(),
            'max_score': cv_scores.max(),
            'individual_scores': cv_scores.tolist()
        }
        
        logger.info(f"CV Mean: {cv_analysis['mean_score']:.4f} (+/- {cv_analysis['std_score']:.4f})")
        return cv_analysis
    
    def compare_models(self, models: Dict[str, Any], X_train, y_train, cv: int = 5):
        """Compare performance of multiple models"""
        comparison_results = {}
        scoring = 'r2' if self.model_type == 'regression' else 'accuracy'
        
        for model_name, model in models.items():
            scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=scoring)
            comparison_results[model_name] = {
                'mean': scores.mean(),
                'std': scores.std(),
                'scores': scores.tolist()
            }
            logger.info(f"{model_name}: {scores.mean():.4f} (+/- {scores.std():.4f})")
        
        return comparison_results
    
    def get_hyperparameter_importance(self) -> Dict:
        """Extract hyperparameter importance from grid search results"""
        if not self.cv_results:
            return {}
        
        importance = {}
        for param, values in self.cv_results.items():
            if 'param_' in param:
                importance[param.replace('param_', '')] = values
        
        return importance
    
    def save_tuning_results(self, filepath: str):
        """Save tuning results to JSON file"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'best_params': self.best_params,
            'best_score': float(self.best_score) if self.best_score else None,
            'model_type': self.model_type,
            'optimization_history': self.optimization_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Tuning results saved to {filepath}")
    
    def get_summary(self) -> Dict:
        """Get summary of tuning results"""
        return {
            'best_model_type': self.model_type,
            'best_params': self.best_params,
            'best_score': self.best_score,
            'num_cv_results': len(self.cv_results),
            'timestamp': datetime.now().isoformat()
        }


class EnsembleOptimizer:
    """Optimize ensemble model combinations"""
    
    def __init__(self):
        self.ensemble_models = {}
        self.ensemble_weights = {}
    
    def voting_classifier(self, base_models: List, voting: str = 'hard'):
        """Create voting classifier ensemble"""
        from sklearn.ensemble import VotingClassifier
        
        ensemble = VotingClassifier(estimators=base_models, voting=voting)
        logger.info(f"Created voting classifier with {len(base_models)} base models")
        return ensemble
    
    def voting_regressor(self, base_models: List):
        """Create voting regressor ensemble"""
        from sklearn.ensemble import VotingRegressor
        
        ensemble = VotingRegressor(estimators=base_models)
        logger.info(f"Created voting regressor with {len(base_models)} base models")
        return ensemble
    
    def stacking(self, base_models: List, meta_model, X_train, y_train, X_test=None):
        """Create stacking ensemble"""
        meta_features_train = np.zeros((X_train.shape[0], len(base_models)))
        
        for i, model in enumerate(base_models):
            model.fit(X_train, y_train)
            meta_features_train[:, i] = model.predict(X_train)
        
        meta_model.fit(meta_features_train, y_train)
        logger.info(f"Created stacking ensemble with {len(base_models)} base models")
        
        return meta_model
    
    def optimize_ensemble_weights(self, base_predictions: List[np.ndarray],
                                 y_true: np.ndarray) -> np.ndarray:
        """Optimize ensemble weights for weighted averaging"""
        from scipy.optimize import minimize
        
        def weighted_mse(weights):
            weighted_pred = np.average(np.array(base_predictions), axis=0, weights=weights)
            return np.mean((weighted_pred - y_true) ** 2)
        
        n_models = len(base_predictions)
        initial_weights = np.ones(n_models) / n_models
        
        result = minimize(weighted_mse, initial_weights,
                        constraints=({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},),
                        bounds=[(0, 1)] * n_models, method='SLSQP')
        
        optimal_weights = result.x
        logger.info(f"Optimal ensemble weights: {optimal_weights}")
        return optimal_weights


if __name__ == "__main__":
    # Example usage
    # tuner = HyperparameterTuner(model_type='regression')
    # df = pd.read_csv('./data/business_data.csv')
    # X = df.drop(columns=['target'])
    # y = df['target']
    # from sklearn.model_selection import train_test_split
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # best_model = tuner.grid_search_regression(X_train, y_train)
    # tuner.save_tuning_results('./tuning_results.json')
    pass
