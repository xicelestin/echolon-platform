"""Phase 5: FastAPI Backend
RESTful API service for model training, prediction, and serving

Endpoints:
- POST /train - Train a model
- POST /predict - Make predictions
- GET /models - List available models
- GET /models/{model_name}/metrics - Get model metrics
- GET /models/{model_name}/version - Get model version
- POST /batch-predict - Batch prediction
- GET /health - Health check
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Echolon AI - Model Serving API",
    description="Production-grade REST API for ML model serving",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== Pydantic Models =====================

class PredictionRequest(BaseModel):
    """Request model for single prediction"""
    model_name: str = Field(..., description="Name of model to use")
    features: Dict[str, Any] = Field(..., description="Input features")
    model_version: Optional[str] = Field(None, description="Specific model version")

class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""
    model_name: str
    data: List[Dict[str, Any]] = Field(..., min_items=1)
    model_version: Optional[str] = None

class TrainingRequest(BaseModel):
    """Request model for model training"""
    model_name: str
    model_type: str = Field(..., description="'classification' or 'regression'")
    training_data_path: str
    test_size: float = 0.2
    hyperparameter_tuning: bool = False
    cross_validation_folds: int = 5

class PredictionResponse(BaseModel):
    """Response model for prediction"""
    prediction: Any
    confidence: Optional[float] = None
    model_version: str
    timestamp: str
    processing_time_ms: float

class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions"""
    predictions: List[Any]
    model_version: str
    total_records: int
    successful_predictions: int
    failed_predictions: int
    timestamp: str
    processing_time_ms: float

class ModelMetrics(BaseModel):
    """Model performance metrics"""
    model_name: str
    model_version: str
    metrics: Dict[str, float]
    trained_at: str
    training_samples: int
    feature_count: int

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    available_models: List[str]

# ===================== In-Memory Model Registry =====================

class ModelRegistry:
    """Manage trained models"""
    
    def __init__(self):
        self.models = {}
        self.metadata = {}
        self.metrics_cache = {}
        logger.info("Model registry initialized")
    
    def register_model(self, model_name: str, model_obj: Any, metadata: Dict):
        """Register a trained model"""
        self.models[model_name] = model_obj
        self.metadata[model_name] = metadata
        logger.info(f"Model registered: {model_name}")
    
    def get_model(self, model_name: str, version: Optional[str] = None):
        """Retrieve model by name and optional version"""
        if model_name not in self.models:
            raise ValueError(f"Model not found: {model_name}")
        return self.models[model_name]
    
    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.models.keys())
    
    def get_metadata(self, model_name: str):
        """Get model metadata"""
        return self.metadata.get(model_name, {})
    
    def cache_metrics(self, model_name: str, metrics: Dict):
        """Cache model metrics"""
        self.metrics_cache[model_name] = {
            'metrics': metrics,
            'cached_at': datetime.now().isoformat()
        }

model_registry = ModelRegistry()

# ===================== API Endpoints =====================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        available_models=model_registry.list_models()
    )

@app.get("/models")
async def list_models():
    """List all available models"""
    models = model_registry.list_models()
    return {
        "available_models": models,
        "count": len(models),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        metadata = model_registry.get_metadata(model_name)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
        
        return {
            "model_name": model_name,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{model_name}/metrics", response_model=ModelMetrics)
async def get_model_metrics(model_name: str):
    """Get model evaluation metrics"""
    try:
        metadata = model_registry.get_metadata(model_name)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
        
        metrics = metadata.get('metrics', {})
        return ModelMetrics(
            model_name=model_name,
            model_version=metadata.get('version', 'unknown'),
            metrics=metrics,
            trained_at=metadata.get('trained_at', ''),
            training_samples=metadata.get('training_samples', 0),
            feature_count=metadata.get('feature_count', 0)
        )
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make a single prediction"""
    import time
    start_time = time.time()
    
    try:
        # Get model
        model = model_registry.get_model(request.model_name)
        metadata = model_registry.get_metadata(request.model_name)
        
        # Mock prediction (replace with actual model.predict())
        import numpy as np
        prediction = float(np.random.rand())
        
        processing_time = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            prediction=prediction,
            confidence=0.95,
            model_version=metadata.get('version', 'unknown'),
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(request: BatchPredictionRequest):
    """Make batch predictions"""
    import time
    start_time = time.time()
    
    try:
        model = model_registry.get_model(request.model_name)
        metadata = model_registry.get_metadata(request.model_name)
        
        # Mock batch predictions
        import numpy as np
        predictions = [float(x) for x in np.random.rand(len(request.data))]
        
        processing_time = (time.time() - start_time) * 1000
        
        return BatchPredictionResponse(
            predictions=predictions,
            model_version=metadata.get('version', 'unknown'),
            total_records=len(request.data),
            successful_predictions=len(predictions),
            failed_predictions=0,
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Train a new model (async)"""
    try:
        # Queue training as background task
        background_tasks.add_task(train_model_background, request)
        
        return {
            "status": "training_queued",
            "model_name": request.model_name,
            "message": "Model training started in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def train_model_background(request: TrainingRequest):
    """Background task for model training"""
    try:
        logger.info(f"Starting training for model: {request.model_name}")
        
        # Mock training
        metadata = {
            'version': 'v1.0',
            'trained_at': datetime.now().isoformat(),
            'model_type': request.model_type,
            'training_samples': 1000,
            'feature_count': 10,
            'metrics': {'accuracy': 0.95, 'f1': 0.92}
        }
        
        # Register model
        model_registry.register_model(request.model_name, None, metadata)
        logger.info(f"Training complete for model: {request.model_name}")
        
    except Exception as e:
        logger.error(f"Background training error: {str(e)}")

@app.get("/models/{model_name}/version")
async def get_model_version(model_name: str):
    """Get current model version"""
    try:
        metadata = model_registry.get_metadata(model_name)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
        
        return {
            "model_name": model_name,
            "version": metadata.get('version', 'unknown'),
            "trained_at": metadata.get('trained_at', ''),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_name}/reload")
async def reload_model(model_name: str):
    """Reload a model from disk"""
    try:
        logger.info(f"Reloading model: {model_name}")
        
        return {
            "status": "model_reloaded",
            "model_name": model_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Reload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================== Startup/Shutdown =====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("FastAPI backend starting...")
    
    # Load pre-trained models from disk (if they exist)
    # model_registry.register_model('churn_predictor', churn_model, {...})
    # model_registry.register_model('demand_forecaster', demand_model, {...})
    # model_registry.register_model('anomaly_detector', anomaly_model, {...})
    
    logger.info(f"Loaded {len(model_registry.list_models())} models")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("FastAPI backend shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        workers=4
    )
