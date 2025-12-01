from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import pandas as pd
import io
from app.schemas import schemas
from app.models.models import BusinessData
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.ml.forecast_service import ForecastService
from app.services.ml.insights_service import InsightsService
from app.services.ml.schemas import ForecastRequest, ForecastResponse, InsightsRequest, InsightsResponse

router = APIRouter()

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), session: Session = Depends(get_db)):
    """Upload CSV file with business data."""
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Parse CSV
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns
        required_cols = ['date', 'metric_name', 'value']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {required_cols}. Missing: {missing_cols}"
            )
        
        # Store in database
        business_data = BusinessData(
            user_id=1,  # TODO: Get from auth context
            filename=file.filename,
            data=df.to_dict('records'),
            data_type='timeseries'
        )
        session.add(business_data)
        session.commit()
        
        return {
            "message": "CSV uploaded successfully",
            "filename": file.filename,
            "rows_processed": len(df),
            "status": "success"
        }
    
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
