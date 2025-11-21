"""Echolon AI - FastAPI Backend Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints
from app.db.database import engine, Base
from app.models.models import User, BusinessData, Metrics, Predictions
# Create database tables
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Echolon AI API",
    description="AI-powered business optimization platform",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints.router, prefix="/api/v1", tags=["main"])

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
