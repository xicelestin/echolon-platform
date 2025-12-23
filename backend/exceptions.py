"""Custom exception classes for Echolon AI error handling.

Provides structured exception hierarchy for different error types:
- Authentication errors
- Database errors
- Data source integration errors
- Validation errors
- Rate limiting errors
- Service errors
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error_code: str
    message: str
    detail: Optional[str] = None
    timestamp: datetime = None
    request_id: Optional[str] = None
    retry_after: Optional[int] = None

    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class EcholonException(Exception):
    """Base exception for all Echolon errors."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        detail: Optional[str] = None,
        status_code: int = 500,
        retry_after: Optional[int] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.detail = detail or message
        self.status_code = status_code
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow()
        super().__init__(message)

    def to_response(self, request_id: Optional[str] = None) -> ErrorResponse:
        """Convert exception to ErrorResponse."""
        return ErrorResponse(
            error_code=self.error_code,
            message=self.message,
            detail=self.detail,
            timestamp=self.timestamp,
            request_id=request_id,
            retry_after=self.retry_after,
        )

    def to_http_exception(self, request_id: Optional[str] = None) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail=self.to_response(request_id).dict(),
        )


class AuthenticationError(EcholonException):
    """Raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication failed", detail: Optional[str] = None):
        super().__init__(
            error_code="AUTH_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(EcholonException):
    """Raised for insufficient permissions."""
    
    def __init__(self, message: str = "Insufficient permissions", detail: Optional[str] = None):
        super().__init__(
            error_code="AUTHZ_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationError(EcholonException):
    """Raised for validation failures."""
    
    def __init__(self, message: str = "Validation failed", detail: Optional[str] = None):
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class DatabaseError(EcholonException):
    """Raised for database operations failures."""
    
    def __init__(self, message: str = "Database error", detail: Optional[str] = None):
        super().__init__(
            error_code="DB_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class DataSourceError(EcholonException):
    """Raised for data source integration errors."""
    
    def __init__(self, message: str = "Data source error", detail: Optional[str] = None, retry_after: Optional[int] = None):
        super().__init__(
            error_code="DATASOURCE_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retry_after=retry_after,
        )


class APIIntegrationError(EcholonException):
    """Raised for external API integration failures."""
    
    def __init__(self, message: str = "API integration error", detail: Optional[str] = None, retry_after: Optional[int] = None):
        super().__init__(
            error_code="API_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retry_after=retry_after,
        )


class RateLimitError(EcholonException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            error_code="RATE_LIMIT_ERROR",
            message=message,
            detail=f"Please retry after {retry_after} seconds",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            retry_after=retry_after,
        )


class ResourceNotFoundError(EcholonException):
    """Raised when requested resource is not found."""
    
    def __init__(self, resource_type: str = "Resource", resource_id: Optional[str] = None):
        detail = f"{resource_type} not found"
        if resource_id:
            detail += f" (ID: {resource_id})"
        super().__init__(
            error_code="NOT_FOUND",
            message=detail,
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TimeoutError(EcholonException):
    """Raised when operation times out."""
    
    def __init__(self, message: str = "Operation timed out", detail: Optional[str] = None, retry_after: int = 30):
        super().__init__(
            error_code="TIMEOUT_ERROR",
            message=message,
            detail=detail or "The operation took too long. Please try again.",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            retry_after=retry_after,
        )


class CircuitBreakerOpenError(EcholonException):
    """Raised when circuit breaker is open."""
    
    def __init__(self, service_name: str = "Service", retry_after: int = 60):
        super().__init__(
            error_code="CIRCUIT_BREAKER_OPEN",
            message=f"{service_name} is temporarily unavailable",
            detail=f"The {service_name} is experiencing issues. Please retry later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retry_after=retry_after,
        )


class StreamlitSessionError(EcholonException):
    """Raised for Streamlit session-related errors."""
    
    def __init__(self, message: str = "Session error", detail: Optional[str] = None):
        super().__init__(
            error_code="SESSION_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DataProcessingError(EcholonException):
    """Raised for data processing failures."""
    
    def __init__(self, message: str = "Data processing error", detail: Optional[str] = None):
        super().__init__(
            error_code="PROCESSING_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ConfigurationError(EcholonException):
    """Raised for configuration-related errors."""
    
    def __init__(self, message: str = "Configuration error", detail: Optional[str] = None):
        super().__init__(
            error_code="CONFIG_ERROR",
            message=message,
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
