from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    company_name: Optional[str] = None
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    company_name: Optional[str]
    is_active: int
    
    class Config:
        from_attributes = True

class BusinessDataCreate(BaseModel):
    data: Any
    data_type: str = "csv"
    filename: Optional[str] = None

class MetricsOut(BaseModel):
    metric_name: str
    metric_value: float
    timestamp: datetime
    metric_category: Optional[str] = None
    
    class Config:
        from_attributes = True

class PredictionsOut(BaseModel):
    prediction_result: Dict
    created_at: datetime
    prediction_type: Optional[str] = None
    confidence_score: Optional[float] = None
    
    class Config:
        from_attributes = True
