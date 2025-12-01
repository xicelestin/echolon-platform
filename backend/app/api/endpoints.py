from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import pandas as pd
import io
from app.schemas import schemas
from app.models.models import BusinessData
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
# Optional ML imports
try:
    from app.services.ml.forecast_service import ForecastService
    from app.services.ml.insights_service import InsightsService
    from app.services.ml.schemas import ForecastRequest, ForecastResponse, InsightsRequest, InsightsResponse
    HAS_ML = True
except ImportError as e:
    print(f"ML services not available: {e}")
    HAS_ML = False
    ForecastService = None
    InsightsService = None

router = APIRouter()

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), session: Session = Depends(get_db)):
    """Upload CSV file with business data. Accepts any CSV with a date column."""
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Parse CSV
        df = pd.read_csv(io.BytesIO(contents))
        
        # Find date column (case-insensitive)
        date_col = None
        for col in df.columns:
            if col.lower() in ['date', 'timestamp', 'time', 'day']:
                date_col = col
                break
        
        if date_col is None:
            raise HTTPException(status_code=400, detail="CSV must contain a 'date' column")
        
        # Normalize date column name to 'date'
        if date_col != 'date':
            df = df.rename(columns={date_col: 'date'})
        
        # Check if already in long format (date, metric_name, value)
        if 'metric_name' in df.columns and 'value' in df.columns:
            data_records = df.to_dict('records')
        else:
            # Wide format - transform to long format for ML compatibility
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if numeric_cols:
                df_long = df.melt(
                    id_vars=['date'],
                    value_vars=numeric_cols,
                    var_name='metric_name',
                    value_name='value'
                )
                data_records = df_long.to_dict('records')
            else:
                data_records = df.to_dict('records')
        
        # Store in database
        business_data = BusinessData(
            user_id=1,  # TODO: Get from auth context
            filename=file.filename,
            data=data_records,
            data_type='timeseries'
        )
        session.add(business_data)
        session.commit()
        
        return {
            "message": "CSV uploaded successfully",
            "filename": file.filename,
            "rows_processed": len(df),
            "columns": list(df.columns),
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV: {str(e)}"
        )

@router.get("/insights", response_model=List[schemas.MetricsOut])
async def get_insights():
    """Get business insights and metrics"""
    # Placeholder: would run analytics and return metrics
    # TODO: Implement analytics engine integration
    placeholder_metrics = [
        schemas.MetricsOut(
            metric_name="Revenue Growth",
            metric_value=15.3,
            timestamp=datetime.now()
        ),
        schemas.MetricsOut(
            metric_name="Customer Acquisition",
            metric_value=342.0,
            timestamp=datetime.now()
        )
    ]
    return placeholder_metrics

@router.get("/predictions", response_model=List[schemas.PredictionsOut])
async def get_predictions():
    """Get AI-generated predictions"""
    # Placeholder: would return predictions based on data
    # TODO: Implement ML model integration
    placeholder_predictions = [
        schemas.PredictionsOut(
            prediction_result={"forecast": "Revenue increase expected", "confidence": 0.87},
            created_at=datetime.now()
        )
    ]
    return placeholder_predictions

# =============================================================================
# ML ENDPOINTS - Machine Learning Forecasting and Insights
# =============================================================================

if HAS_ML:
    @router.post("/ml/forecast", response_model=ForecastResponse)
    def create_forecast(request: ForecastRequest, session: Session = Depends(get_db)):
        """Generate ML forecast for a specific business metric."""
        service = ForecastService()
        return service.generate_forecast(session, request)

    @router.post("/ml/insights", response_model=InsightsResponse)
    def generate_insights(request: InsightsRequest):
        """Generate AI-powered business insights from forecast data."""
        return InsightsService.generate_insights(request)

    @router.post("/ml/train/{business_id}/{metric_name}")
    def train_model(business_id: int, metric_name: str, model_type: str = "auto", session: Session = Depends(get_db)):
        """Train ML model for a specific business and metric."""
        service = ForecastService()
        result = service.train_model(session, business_id, metric_name, model_type)
        return {
            "message": "Model training completed",
            "business_id": business_id,
            "metric_name": metric_name,
            "model_type": result["model_type"],
            "accuracy": result.get("accuracy", 0.0)
        }
else:
    @router.post("/ml/forecast")
    def create_forecast_unavailable():
        """ML services not available."""
        raise HTTPException(status_code=503, detail="ML services not available. Install XGBoost/Prophet dependencies.")
    
    @router.post("/ml/insights")
    def generate_insights_unavailable():
        """ML services not available."""
        raise HTTPException(status_code=503, detail="ML services not available. Install required dependencies.")
    
    @router.post("/ml/train/{business_id}/{metric_name}")
    def train_model_unavailable(business_id: int, metric_name: str):
        """ML services not available."""
        raise HTTPException(status_code=503, detail="ML services not available. Install required dependencies.")
