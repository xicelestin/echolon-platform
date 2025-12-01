"""Pydantic schemas for ML forecasting requests and responses."""

from pydantic import BaseModel, Field
from datetime import date as date_type
from typing import Optional, List


class ForecastRequest(BaseModel):
    """Request schema for forecast generation."""
    business_id: int = Field(..., description="ID of the business")
    metric_name: str = Field(..., description="Name of the metric to forecast")
    horizon: int = Field(30, description="Forecast horizon in days", ge=1, le=365)
    model_type: Optional[str] = Field("auto", description="Model type: 'xgboost', 'prophet', or 'auto'")


class ForecastPoint(BaseModel):
    """Individual forecast data point."""
    date: date_type = Field(..., description="Date of the forecast")
    value: float = Field(..., description="Predicted value")
    lower_bound: Optional[float] = Field(None, description="Lower confidence bound")
    upper_bound: Optional[float] = Field(None, description="Upper confidence bound")


class ForecastResponse(BaseModel):
    """Response schema for forecast results."""
    business_id: int
    metric_name: str
    horizon: int
    model_used: str = Field(..., description="Model that was used: 'xgboost' or 'prophet'")
    points: List[ForecastPoint] = Field(..., description="List of forecast points")
    metrics: Optional[dict] = Field(None, description="Model performance metrics")


class InsightsRequest(BaseModel):
    """Request schema for AI insights generation."""
    business_id: int = Field(..., description="ID of the business")
    metric_name: str = Field(..., description="Name of the metric to analyze")
    forecast_data: Optional[List[ForecastPoint]] = Field(None, description="Forecast data for context")
    historical_summary: Optional[dict] = Field(None, description="Historical data summary")


class InsightsResponse(BaseModel):
    """Response schema for AI insights."""
    business_id: int
    metric_name: str
    insights: str = Field(..., description="AI-generated insights and recommendations")
    key_findings: List[str] = Field(..., description="Key findings and trends")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
