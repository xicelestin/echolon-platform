import numpy as np
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
from sklearn.model_selection import cross_val_score
from xgboost import XGBRegressor
import pandas as pd


class HyperparameterTuner:
    """
    Bayesian hyperparameter optimization using Optuna for XGBoost models.
    
    Uses Tree-structured Parzen Estimator (TPE) sampler for efficient
    exploration of the hyperparameter space.
    """
    
    def __init__(self, X_train, y_train, X_val=None, y_val=None, n_trials=50, timeout=300):
        """
        Initialize hyperparameter tuner.
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Training targets (n_samples,)
            X_val: Validation features for early stopping (optional)
            y_val: Validation targets for early stopping (optional)
            n_trials: Number of optimization trials (default: 50)
            timeout: Maximum time in seconds for optimization (default: 300)
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.n_trials = n_trials
        self.timeout = timeout
        self.best_params = None
        self.best_score = None
        self.study = None
        self.optimization_history = []
        
    def objective(self, trial):
        """
        Objective function for Optuna optimization.
        Defines hyperparameter search space and evaluation metric.
        
        Args:
            trial: Optuna trial object
            
        Returns:
            Negative RMSE (for maximization)
        """
        # Define search space for XGBoost hyperparameters
        params = {
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 50, 500, step=50),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.5, 1.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'gamma': trial.suggest_float('gamma', 0, 5.0),
            'lambda': trial.suggest_float('lambda', 0.1, 5.0),
            'alpha': trial.suggest_float('alpha', 0.1, 5.0),
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Cross-validation scoring
        model = XGBRegressor(**params)
        
        if self.X_val is not None and self.y_val is not None:
            # Use validation set if provided
            model.fit(self.X_train, self.y_train, verbose=False)
            from sklearn.metrics import mean_squared_error
            from math import sqrt
            rmse = sqrt(mean_squared_error(self.y_val, model.predict(self.X_val)))
            return -rmse  # Negative because Optuna maximizes
        else:
            # Use 5-fold cross-validation
            scores = cross_val_score(
                model, self.X_train, self.y_train,
                cv=5, scoring='neg_mean_squared_error', n_jobs=-1
            )
            return np.mean(scores)  # Already negative from scoring metric
    
    def optimize(self, show_progress_bar=True):
        """
        Run hyperparameter optimization.
        
        Args:
            show_progress_bar: Whether to display progress bar
            
        Returns:
            Dictionary of best hyperparameters
        """
        # Create study with TPE sampler and median pruner
        sampler = TPESampler(seed=42)
        pruner = MedianPruner(n_warmup_steps=5)
        
        self.study = optuna.create_study(
            direction='maximize',
            sampler=sampler,
            pruner=pruner
        )
        
        # Optimize
        self.study.optimize(
            self.objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=show_progress_bar
        )
        
        # Extract best parameters
        self.best_params = self.study.best_params
        self.best_score = self.study.best_value
        self.optimization_history = self._extract_history()
        
        return self.best_params
    
    def _extract_history(self):
        """
        Extract optimization history for analysis.
        
        Returns:
            List of trial results with scores and parameters
        """
        history = []
        for trial in self.study.trials:
            history.append({
                'trial_number': trial.number,
                'score': trial.value,
                'status': trial.state.name,
                'params': trial.params
            })
        return history
    
    def get_best_params(self):
        """
        Get the best hyperparameters found.
        
        Returns:
            Dictionary of hyperparameters with best score
        """
        if self.best_params is None:
            raise ValueError("Optimization not yet performed. Call optimize() first.")
        
        return {
            'params': self.best_params,
            'score': self.best_score
        }
    
    def get_importance(self):
        """
        Analyze hyperparameter importance based on optimization trials.
        
        Returns:
            DataFrame with parameter importance scores
        """
        if self.study is None:
            raise ValueError("Optimization not yet performed. Call optimize() first.")
        
        try:
            importance = optuna.importance.get_param_importances(self.study)
            importance_df = pd.DataFrame(
                list(importance.items()),
                columns=['parameter', 'importance']
            ).sort_values('importance', ascending=False)
            return importance_df
        except Exception as e:
            print(f"Could not compute importance: {e}")
            return None
    
    def get_optimization_history(self):
        """
        Get the complete optimization history.
        
        Returns:
            DataFrame with trial results
        """
        if not self.optimization_history:
            raise ValueError("No optimization history available.")
        
        return pd.DataFrame(self.optimization_history)
    
    def suggest_sample_size(self):
        """
        Recommend sample size based on number of hyperparameters.
        
        Returns:
            Recommended number of trials
        """
        # Heuristic: 10-20 trials per hyperparameter
        n_params = len(self.best_params) if self.best_params else 10
        return max(50, n_params * 15)


def quick_tune(X_train, y_train, n_trials=30):
    """
    Quick hyperparameter tuning with sensible defaults.
    
    Args:
        X_train: Training features
        y_train: Training targets
        n_trials: Number of trials (default: 30)
        
    Returns:
        Dictionary with best parameters and score
    """
    tuner = HyperparameterTuner(X_train, y_train, n_trials=n_trials)
    best_params = tuner.optimize(show_progress_bar=True)
    return tuner.get_best_params()
