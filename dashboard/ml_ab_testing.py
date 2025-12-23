"""A/B Testing Module - Validate predictions vs actuals

Features:
- A/B test framework
- Statistical significance testing
- Prediction validation
- Performance comparison
"""

import numpy as np
from scipy import stats
from typing import Dict, List

class ABTestingFramework:
    """A/B testing for ML predictions"""
    
    def __init__(self):
        self.tests_run = []
        self.significance_level = 0.05
    
    def compare_predictions(self, model_a: List[float], model_b: List[float], actuals: List[float]) -> Dict:
        """Compare two model predictions against actuals"""
        model_a = np.array(model_a)
        model_b = np.array(model_b)
        actuals = np.array(actuals)
        
        # Calculate metrics for each model
        mae_a = np.mean(np.abs(model_a - actuals))
        mae_b = np.mean(np.abs(model_b - actuals))
        rmse_a = np.sqrt(np.mean((model_a - actuals) ** 2))
        rmse_b = np.sqrt(np.mean((model_b - actuals) ** 2))
        
        # T-test for statistical significance
        errors_a = model_a - actuals
        errors_b = model_b - actuals
        t_stat, p_value = stats.ttest_ind(errors_a, errors_b)
        
        is_significant = p_value < self.significance_level
        winner = 'model_a' if mae_a < mae_b else 'model_b'
        
        return {
            'model_a_mae': float(mae_a),
            'model_b_mae': float(mae_b),
            'model_a_rmse': float(rmse_a),
            'model_b_rmse': float(rmse_b),
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'is_significant': is_significant,
            'winner': winner,
            'improvement': float((mae_a - mae_b) / mae_a * 100) if mae_a > 0 else 0
        }
    
    def run_ab_test(self, test_name: str, model_a: List[float], model_b: List[float], actuals: List[float]) -> Dict:
        """Run A/B test and log results"""
        results = self.compare_predictions(model_a, model_b, actuals)
        results['test_name'] = test_name
        self.tests_run.append(results)
        return results
    
    def get_test_history(self) -> List[Dict]:
        """Get history of all tests run"""
        return self.tests_run

ab_testing = ABTestingFramework()

def run_ab_test(test_name: str, predictions_a: List[float], predictions_b: List[float], actuals: List[float]) -> Dict:
    """Run A/B test comparing two predictions"""
    return ab_testing.run_ab_test(test_name, predictions_a, predictions_b, actuals)
