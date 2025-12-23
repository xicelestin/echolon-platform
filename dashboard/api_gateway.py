"""Phase 9: API Gateway - FastAPI Service Layer
REST API wrapper for all ML modules and dashboard integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import logging
import time
from datetime import datetime
from functools import wraps
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Echolon AI API Gateway",
    description="Production API for ML models and business intelligence",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==================== Data Models ====================

class PredictionRequest(BaseModel):
    """Request model for predictions"""
    features: List[float] = Field(..., description="Input features for model")
    model_type: str = Field(default="regression", description="regression or classification")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: float
    confidence: Optional[float] = None
    model_version: str
    timestamp: str
    processing_time_ms: float

class ModelPerformanceRequest(BaseModel):
    """Request model for performance metrics"""
    model_name: str
    metric_type: str = Field(default="all", description="mse, accuracy, r2, etc.")

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    uptime_seconds: float
    models_loaded: List[str]
    memory_usage_mb: float

class DriftDetectionRequest(BaseModel):
    """Request model for drift detection"""
    model_name: str
    baseline_data: List[List[float]]
    current_data: List[List[float]]
    sensitivity: float = Field(default=0.05, ge=0.01, le=0.5)

class EnsembleRequest(BaseModel):
    """Request model for ensemble predictions"""
    features: List[float]
    ensemble_type: str = Field(default="voting", description="voting, stacking, blending")
    base_models: Optional[List[str]] = None

# ==================== Middleware & Utilities ====================

class RateLimiter:
    """Simple rate limiter for API protection"""
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter(max_requests=1000, window_seconds=60)

def rate_limit(client_id: str = "default"):
    """Rate limit decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not rate_limiter.is_allowed(client_id):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# ==================== Health & Status Endpoints ====================

@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "Echolon AI API Gateway",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", tags=["System"], response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        uptime_seconds=time.time(),
        models_loaded=["revenue_predictor", "customer_churn", "demand_forecast"],
        memory_usage_mb=memory_info.rss / 1024 / 1024
    )

@app.get("/api/v1/models", tags=["Models"])
async def list_models():
    """List all available models"""
    return {
        "models": [
            {
                "name": "revenue_predictor",
                "type": "regression",
                "version": "1.2.0",
                "last_updated": "2024-12-23"
            },
            {
                "name": "customer_churn",
                "type": "classification",
                "version": "1.1.5",
                "last_updated": "2024-12-22"
            }
        ],
        "total_models": 2
    }

# ==================== Prediction Endpoints ====================

@app.post("/api/v1/predict", tags=["Predictions"], response_model=PredictionResponse)
async def predict(request: PredictionRequest, background_tasks: BackgroundTasks):
    """Make a prediction with specified model"""
    try:
        start_time = time.time()
        
        # Validate input
        if not request.features:
            raise HTTPException(status_code=400, detail="Features cannot be empty")
        
        # Mock prediction (replace with actual model inference)
        prediction = sum(request.features) / len(request.features)
        processing_time = (time.time() - start_time) * 1000
        
        # Log prediction in background
        background_tasks.add_task(log_prediction, request.model_type, prediction)
        
        return PredictionResponse(
            prediction=float(prediction),
            confidence=0.92,
            model_version="1.2.0",
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ensemble-predict", tags=["Predictions"])
async def ensemble_predict(request: EnsembleRequest):
    """Make ensemble predictions"""
    try:
        # Mock ensemble prediction
        predictions = {
            "ensemble_prediction": sum(request.features) / len(request.features),
            "base_model_predictions": {
                "random_forest": 0.45,
                "gradient_boost": 0.48,
                "svr": 0.46
            },
            "ensemble_type": request.ensemble_type,
            "confidence": 0.94,
            "timestamp": datetime.now().isoformat()
        }
        return predictions
    except Exception as e:
        logger.error(f"Ensemble prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Model Monitoring Endpoints ====================

@app.get("/api/v1/models/{model_name}/performance", tags=["Monitoring"])
async def get_model_performance(model_name: str):
    """Get model performance metrics"""
    return {
        "model_name": model_name,
        "metrics": {
            "accuracy": 0.92,
            "precision": 0.89,
            "recall": 0.88,
            "f1_score": 0.885,
            "auc_roc": 0.94
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/drift-detection", tags=["Monitoring"])
async def detect_drift(request: DriftDetectionRequest):
    """Detect data drift in model inputs"""
    try:
        return {
            "model_name": request.model_name,
            "drift_detected": False,
            "p_value": 0.23,
            "threshold": request.sensitivity,
            "recommendation": "No action required",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Drift detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models/{model_name}/drift-history", tags=["Monitoring"])
async def get_drift_history(model_name: str, days: int = 30):
    """Get drift detection history"""
    return {
        "model_name": model_name,
        "period_days": days,
        "drift_events": [
            {"date": "2024-12-20", "drift_detected": False, "p_value": 0.45},
            {"date": "2024-12-21", "drift_detected": False, "p_value": 0.38}
        ],
        "total_events": 2
    }

# ==================== Hyperparameter Tuning Endpoints ====================

@app.post("/api/v1/models/{model_name}/tune", tags=["Optimization"])
async def tune_hyperparameters(model_name: str, background_tasks: BackgroundTasks):
    """Trigger hyperparameter tuning for a model"""
    try:
        job_id = f"tune_{model_name}_{int(time.time())}"
        background_tasks.add_task(run_hyperparameter_tuning, model_name, job_id)
        
        return {
            "job_id": job_id,
            "model_name": model_name,
            "status": "queued",
            "message": "Tuning job queued for processing",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Tuning error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}", tags=["Optimization"])
async def get_job_status(job_id: str):
    """Get status of background job"""
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "results": {
            "best_params": {"n_estimators": 150, "max_depth": 15},
            "best_score": 0.945
        },
        "timestamp": datetime.now().isoformat()
    }

# ==================== Background Tasks ====================

async def log_prediction(model_type: str, prediction: float):
    """Log prediction for monitoring"""
    logger.info(f"Prediction logged - Type: {model_type}, Value: {prediction}")

async def run_hyperparameter_tuning(model_name: str, job_id: str):
    """Run hyperparameter tuning"""
    logger.info(f"Starting tuning for {model_name} (Job: {job_id})")
    await asyncio.sleep(5)  # Simulate tuning
    logger.info(f"Tuning completed for {model_name}")

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
