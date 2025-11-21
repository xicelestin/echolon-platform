# Echolon AI ML Engine Implementation Guide

## ✅ Completed Components

### 1. Package Structure
- ✅ `__init__.py` - Package initialization with exports
- ✅ `config.py` - Configuration for XGBoost, Prophet, and OpenAI
- ✅ `schemas.py` - Pydantic schemas for requests/responses
- ✅ `preprocessing.py` - Data loading and feature engineering

### Key Features Implemented:
- Time-series data loading from BusinessData table
- Data cleaning (deduplication, sorting, missing value handling)
- Date-based feature engineering (day_of_week, month, etc.)
- Lag features (1, 7, 14, 30 days)
- Rolling window features (7, 14, 30 day averages/std)
- Separate preparation functions for XGBoost and Prophet

## 🚧 Remaining Implementation

### 2. XGBoost Model (`models_xgboost.py`)

**Required Functions:**
```python
def train_xgboost_model(session, business_id, metric_name, horizon):
    # 1. Load preprocessed data using preprocessing.prepare_data_for_xgboost()
    # 2. Split into train/test
    # 3. Train XGBoost regressor with config.XGBOOST_CONFIG
    # 4. Save model to config.MODELS_STORE_DIR/xgboost_{business_id}_{metric_name}.json
    # 5. Return model path

def predict_xgboost(session, business_id, metric_name, horizon):
    # 1. Load saved model
    # 2. Get latest data for features
    # 3. Generate future dates
    # 4. Create features for future dates
    # 5. Predict values
    # 6. Return List[ForecastPoint]
```

**Dependencies:** `xgboost`, `sklearn`

### 3. Prophet Model (`models_prophet.py`)

**Required Functions:**
```python
def train_prophet_model(session, business_id, metric_name, horizon):
    # 1. Load data using preprocessing.prepare_data_for_prophet()
    # 2. Create Prophet model with config.PROPHET_CONFIG
    # 3. Fit model
    # 4. Save model (pickle)
    # 5. Return model path

def predict_prophet(session, business_id, metric_name, horizon):
    # 1. Load saved Prophet model
    # 2. Create future dataframe
    # 3. Make predictions
    # 4. Extract yhat, yhat_lower, yhat_upper
    # 5. Return List[ForecastPoint]
```

**Dependencies:** `prophet`

### 4. Forecast Service (`forecast_service.py`)

**Main Service Class:**
```python
class ForecastService:
    def generate_forecast(session, request: ForecastRequest) -> ForecastResponse:
        # 1. Choose model (auto, xgboost, or prophet)
        # 2. Check if model exists, train if not
        # 3. Generate predictions
        # 4. Return ForecastResponse with points
```

### 5. Insights Service (`insights_service.py`)

**OpenAI Integration:**
```python
class InsightsService:
    def generate_insights(request: InsightsRequest) -> InsightsResponse:
        # 1. Prepare context from historical data
        # 2. Format forecast data if provided
        # 3. Create prompt for OpenAI
        # 4. Call OpenAI API with config.OPENAI_MODEL
        # 5. Parse response into insights, findings, recommendations
        # 6. Return InsightsResponse
```

**Dependencies:** `openai`

### 6. FastAPI Routes (`backend/app/api/endpoints.py`)

**New ML Endpoints:**
```python
@router.post("/ml/forecast", response_model=ForecastResponse)
def create_forecast(request: ForecastRequest, session: Session = Depends(get_db)):
    service = ForecastService()
    return service.generate_forecast(session, request)

@router.post("/ml/insights", response_model=InsightsResponse)
def generate_insights(request: InsightsRequest):
    service = InsightsService()
    return service.generate_insights(request)

@router.post("/ml/train/{business_id}/{metric_name}")
def train_model(business_id: int, metric_name: str, model_type: str = "auto", session: Session = Depends(get_db)):
    # Train specific model
    pass
```

### 7. Dependencies (`backend/requirements.txt`)

**Add ML Dependencies:**
```
xgboost==2.0.3
prophet==1.1.5
openai==1.0.0
scikit-learn==1.3.2
pandas==2.1.0
numpy==1.24.3
```

## 📋 Implementation Steps

1. **Complete Model Files:** Create models_xgboost.py and models_prophet.py
2. **Build Services:** Implement forecast_service.py and insights_service.py  
3. **Add API Routes:** Update endpoints.py with ML routes
4. **Update Requirements:** Add ML dependencies to requirements.txt
5. **Create models_store Directory:** Ensure models can be saved
6. **Test Integration:** Test end-to-end with sample data
7. **Add Error Handling:** Robust error handling for production

## 🔧 Configuration Notes

- Set `OPENAI_API_KEY` environment variable
- Adjust `MIN_TRAINING_SAMPLES` in config.py based on your needs
- Tune XGBoost and Prophet hyperparameters in config.py
- Create `backend/app/services/ml/models_store/` directory

## 📦 Project Structure

```
backend/app/services/ml/
├── __init__.py ✅
├── config.py ✅
├── schemas.py ✅
├── preprocessing.py ✅
├── models_xgboost.py 🚧
├── models_prophet.py 🚧
├── forecast_service.py 🚧
├── insights_service.py 🚧
└── models_store/ (create this directory)
```

## 🎯 Next Steps

1. Complete the 4 remaining Python files as outlined above
2. Update requirements.txt
3. Add ML endpoints to endpoints.py
4. Test with sample business data
5. Deploy and monitor performance

---

**Status:** Core ML infrastructure complete. Model implementations and API integration remaining.
