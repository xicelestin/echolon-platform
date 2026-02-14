"""Echolon AI - FastAPI Backend Entry Point"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints
from app.api.stripe_webhook import router as stripe_router
from app.db.database import engine, Base
from app.models.models import User, BusinessData, Metrics, Predictions
from error_handling import setup_error_handling

# Create database tables (skip if DB unavailable, e.g. SQLite path issues)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    import logging
    logging.warning(f"Could not create DB tables: {e}. API will run but DB features may fail.")

app = FastAPI(
    title="Echolon AI API",
    description="AI-powered business optimization platform",
    version="1.0.0"
)

# CORS Configuration - use ALLOWED_ORIGINS env in production (e.g. http://localhost:8501,https://your-app.com)
_origins = os.getenv("ALLOWED_ORIGINS", "*")
_origins_list = [o.strip() for o in _origins.split(",")] if _origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handling middleware and exception handlers
setup_error_handling(app)

# Include routers
app.include_router(endpoints.router, prefix="/api/v1", tags=["main"])
app.include_router(stripe_router, prefix="/api/v1/stripe", tags=["stripe"])

@app.get("/")
async def root():
    return {
        "message": "Echolon AI API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
