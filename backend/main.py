"""Echolon AI - FastAPI Backend Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.db.database import engine
from app.models import user, business_data, metrics, predictions

# Create database tables
user.Base.metadata.create_all(bind=engine)
business_data.Base.metadata.create_all(bind=engine)
metrics.Base.metadata.create_all(bind=engine)
predictions.Base.metadata.create_all(bind=engine)

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
app.include_router(routes.router, prefix="/api/v1", tags=["main"])

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
