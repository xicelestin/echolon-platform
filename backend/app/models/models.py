from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    """User model for authentication and business owners"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    business_data = relationship("BusinessData", back_populates="user")

class BusinessData(Base):
    """Store uploaded business data"""
    __tablename__ = "business_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String)
    data = Column(JSON)
    data_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="business_data")
    metrics = relationship("Metrics", back_populates="business_data")
    predictions = relationship("Predictions", back_populates="business_data")

class Metrics(Base):
    """Store calculated business metrics"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    business_data_id = Column(Integer, ForeignKey("business_data.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float)
    metric_category = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)
    
    business_data = relationship("BusinessData", back_populates="metrics")

class Predictions(Base):
    """Store AI-generated predictions"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    business_data_id = Column(Integer, ForeignKey("business_data.id"), nullable=False)
    prediction_type = Column(String)
    prediction_result = Column(JSON)
    confidence_score = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    business_data = relationship("BusinessData", back_populates="predictions")
