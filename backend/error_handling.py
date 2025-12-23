"""Error handling middleware and utilities for FastAPI.

Provides:
- Global exception handlers
- Request ID tracking
- Error logging and monitoring
- Response formatting
- HTTP status code mapping
"""

import logging
import uuid
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from exceptions import EcholonException

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Add request ID to request and response."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling and logging."""
    
    async def dispatch(self, request: Request, call_next):
        """Handle errors and log request/response."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        try:
            start_time = datetime.utcnow()
            response = await call_next(request)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Log successful requests
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Status: {response.status_code} ({duration:.3f}s)"
            )
            
            return response
        
        except EcholonException as e:
            # Handle custom exceptions
            logger.error(
                f"[{request_id}] EcholonException: {e.error_code} - {e.message}",
                exc_info=e,
            )
            return FastAPIJSONResponse(
                status_code=e.status_code,
                content=e.to_response(request_id).dict(),
            )
        
        except Exception as e:
            # Handle unexpected errors
            logger.error(
                f"[{request_id}] Unexpected error: {str(e)}",
                exc_info=e,
            )
            return FastAPIJSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "detail": str(e) if logger.level == logging.DEBUG else None,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )


def register_exception_handlers(app: FastAPI):
    """Register global exception handlers with FastAPI.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(EcholonException)
    async def echolon_exception_handler(
        request: FastAPIRequest,
        exc: EcholonException,
    ):
        """Handle Echolon exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            f"[{request_id}] {exc.error_code}: {exc.message}",
            exc_info=exc,
        )
        return FastAPIJSONResponse(
            status_code=exc.status_code,
            content=exc.to_response(request_id).dict(),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: FastAPIRequest,
        exc: RequestValidationError,
    ):
        """Handle validation errors."""
        request_id = getattr(request.state, "request_id", "unknown")
        errors = [
            {
                "field": ".".join(str(x) for x in err["loc"][1:]),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        logger.warning(
            f"[{request_id}] Validation error: {errors}"
        )
        return FastAPIJSONResponse(
            status_code=422,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "detail": errors,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: FastAPIRequest,
        exc: Exception,
    ):
        """Handle all other exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            f"[{request_id}] Unhandled exception: {str(exc)}",
            exc_info=exc,
        )
        return FastAPIJSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


def setup_error_handling(app: FastAPI):
    """Configure all error handling for an app.
    
    Args:
        app: FastAPI application instance
    """
    # Add middleware (in reverse order, they execute in order added)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    logger.info("Error handling configured")


class ErrorHandler:
    """Utility class for error handling operations."""
    
    @staticmethod
    def get_error_code(exception: Exception) -> str:
        """Get error code from exception.
        
        Args:
            exception: Exception instance
            
        Returns:
            Error code string
        """
        if isinstance(exception, EcholonException):
            return exception.error_code
        return "INTERNAL_SERVER_ERROR"
    
    @staticmethod
    def format_error_response(
        error_code: str,
        message: str,
        detail: Optional[str] = None,
        request_id: Optional[str] = None,
        status_code: int = 500,
    ) -> Dict[str, Any]:
        """Format error response.
        
        Args:
            error_code: Error code
            message: Error message
            detail: Error detail
            request_id: Request ID
            status_code: HTTP status code
            
        Returns:
            Formatted error response dict
        """
        return {
            "error_code": error_code,
            "message": message,
            "detail": detail,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code,
        }
    
    @staticmethod
    def should_retry(exception: Exception) -> bool:
        """Determine if exception is retryable.
        
        Args:
            exception: Exception to check
            
        Returns:
            True if retryable, False otherwise
        """
        if isinstance(exception, EcholonException):
            # Retryable status codes: 408, 429, 500, 502, 503, 504
            return exception.status_code in [
                408,  # Request Timeout
                429,  # Too Many Requests
                500,  # Internal Server Error
                502,  # Bad Gateway
                503,  # Service Unavailable
                504,  # Gateway Timeout
            ]
        return False


def with_error_handling(
    fallback_value: Any = None,
    log_level: str = "error",
):
    """Decorator for functions with error handling.
    
    Args:
        fallback_value: Value to return on error
        log_level: Logging level for errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log_fn = getattr(logger, log_level)
                log_fn(f"Error in {func.__name__}: {str(e)}", exc_info=e)
                return fallback_value
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_fn = getattr(logger, log_level)
                log_fn(f"Error in {func.__name__}: {str(e)}", exc_info=e)
                return fallback_value
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
