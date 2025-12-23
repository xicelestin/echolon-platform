# Phase 6: ML Model Fine-tuning & Custom Features - Implementation Guide

## Overview
Phase 6 brings advanced machine learning capabilities and custom feature engineering to the Echolon AI platform. These modules enable fine-tuning models on actual business data and creating domain-specific features that drive better insights.

## New Modules

### 1. ML Model Fine-tuning Module (`ml_fine_tuning.py`)

Provides comprehensive ML model training and validation on business data.

**Key Features:**
- Data loading and validation
- Automatic data preprocessing (missing values, outlier removal)
- Regression model training (RandomForest)
- Classification model training (GradientBoosting)
- Feature importance extraction
- Model persistence and evaluation metrics

**Class: MLModelFineTuning**
```python
fine_tuner = MLModelFineTuning('./data/business_data.csv')
df = fine_tuner.load_business_data()
metrics = fine_tuner.fine_tune_pipeline(df, target_column='revenue')
fine_tuner.save_models('./ml_models')
```

**Methods:**
- `load_business_data()`: Load CSV data with validation
- `preprocess_data()`: Handle missing values and outliers
- `train_regression_model()`: Train continuous value predictors
- `train_classification_model()`: Train categorical predictors
- `get_feature_importance()`: Extract feature rankings
- `save_models()`: Persist trained models and metrics
- `fine_tune_pipeline()`: Complete end-to-end training flow

**Output Metrics:**
- Regression: MSE, RMSE, R² Score
- Classification: Accuracy, Detailed Classification Report

---

### 2. Custom Features Engineering Module (`custom_features.py`)

Generates business-specific features from raw data to enhance model performance.

**Feature Types:**

#### Temporal Features
- Year, Month, Quarter, Day of Week
- Weekend indicator
- Week of year, Day of month
- Perfect for seasonality and cyclical patterns

#### Aggregation Features
- Rolling means and standard deviations (7-day windows)
- Cumulative sums
- Percentage change rates
- Captures trends and momentum

#### Interaction Features
- Multiplication, Division, Sum, Difference
- Multi-way feature combinations
- Captures non-linear relationships

#### Categorical Features
- Frequency encoding
- Label encoding
- Creates numerical representations of categories

#### Business Logic Features
- Revenue percentiles and high-value segmentation
- Engagement scores
- Churn risk indicators
- Domain-specific calculations

#### Polynomial Features
- Squared, cubed features
- Captures polynomial relationships

**Class: CustomFeatureEngineering**
```python
feature_engineer = CustomFeatureEngineering()
df = pd.read_csv('business_data.csv')
df = feature_engineer.complete_feature_pipeline(
    df,
    date_col='transaction_date',
    agg_cols=['revenue', 'units_sold'],
    cat_cols=['product_category', 'region']
)
summary = feature_engineer.get_feature_summary()
```

---

## Integration with Dashboard

### Dashboard Updates
1. Add ML model training section to dashboard
2. Display model performance metrics
3. Show feature importance visualizations
4. Provide custom feature generation interface

### Required Data Format
```csv
id,date,revenue,category,engagement,last_purchase_days_ago
1,2024-01-15,5000,Electronics,0.8,15
2,2024-01-16,3200,Home,0.6,45
```

---

## Configuration

### ML Fine-tuning Parameters
- Train/Test Split: 80/20
- Random Forest: 100 estimators
- Gradient Boosting: 100 estimators
- Feature scaling: StandardScaler

### Custom Features Parameters
- Rolling window: 7 days
- Polynomial degree: 2
- Outlier threshold: IQR 1.5x

---

## Usage Examples

### Example 1: Fine-tune on Business Data
```python
from ml_fine_tuning import MLModelFineTuning

fine_tuner = MLModelFineTuning('./data/sales_data.csv')
df = fine_tuner.load_business_data()
metrics = fine_tuner.fine_tune_pipeline(df, 'monthly_revenue')

print(f"Model Performance:")
print(f"  RMSE: {metrics['regression']['rmse']:.2f}")
print(f"  R² Score: {metrics['regression']['r2_score']:.4f}")

fine_tuner.save_models('./production_models')
```

### Example 2: Generate Custom Features
```python
from custom_features import CustomFeatureEngineering

engineering = CustomFeatureEngineering()
df = pd.read_csv('business_data.csv')

df = engineering.complete_feature_pipeline(
    df,
    date_col='transaction_date',
    agg_cols=['revenue', 'customer_count'],
    cat_cols=['market_segment', 'product_line']
)

summary = engineering.get_feature_summary()
print(f"Total Features Created: {summary['total_features']}")
print(f"Feature Groups: {summary['feature_groups']}")
```

---

## Performance & Optimization

### Model Training
- Automatic hyperparameter tuning ready
- Parallel processing (n_jobs=-1)
- Feature scaling for numerical stability
- Cross-validation recommended for production

### Feature Engineering
- Efficient pandas operations
- Memory-conscious rolling calculations
- Automatic null handling
- Scalable to large datasets

---

## Testing & Validation

### Recommended Test Cases
1. Load various data formats (CSV, JSON)
2. Handle missing values and duplicates
3. Test edge cases (empty data, single row)
4. Validate model persistence and loading
5. Verify feature calculations on sample data

---

## Next Steps (Phase 7)
1. Advanced hyperparameter optimization (GridSearch, Bayesian)
2. Model ensemble techniques
3. Feature selection algorithms
4. Real-time model monitoring
5. Automated retraining triggers

---

## Troubleshooting

### Common Issues

**Issue**: Insufficient data error
- **Solution**: Ensure minimum 100 samples for training

**Issue**: Feature importance all zeros
- **Solution**: Check for feature scaling and data distribution

**Issue**: Model overfitting
- **Solution**: Reduce model complexity or increase training data

**Issue**: Feature engineering creates NaN values
- **Solution**: Adjust rolling window parameters or use forward fill

---

## Support & Documentation
- See `API_SPECS.md` for complete API reference
- Review `IMPLEMENTATION_ROADMAP.md` for architecture details
- Check `ml_models/` directory for saved model details

---

**Last Updated**: Phase 6 Completion
**Status**: Production Ready
**Maintainer**: Echolon AI Development Team
