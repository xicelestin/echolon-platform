"""Minimal FastAPI Backend for Testing - No Database, Minimal Imports"""
import os
import logging
from fastapi import FastAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting Echolon API - Minimal Version")
logger.info(f"Python version: {os.sys.version}")
logger.info(f"PORT environment variable: {os.getenv('PORT', 'Not set')}")

# Create FastAPI app
app = FastAPI(
    title="Echolon AI API - Minimal",
    description="Minimal test version for debugging deployment",
    version="0.1.0-minimal"
)

logger.info("FastAPI app created successfully")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {
        "message": "Echolon AI API - Minimal Version",
        "status": "running",
        "version": "0.1.0-minimal",
        "environment": {
            "port": os.getenv("PORT", "8080"),
            "log_level": os.getenv("LOG_LEVEL", "info")
        }
    }

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "version": "0.1.0-minimal"
    }

@app.get("/test")
async def test():
    logger.info("Test endpoint called")
    return {
        "message": "Test endpoint working",
        "imports": [
            "os",
            "logging",
            "fastapi"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
