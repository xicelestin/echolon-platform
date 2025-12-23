# Phase 9: Error Handling & Resilience

## Overview

Phase 9 implements comprehensive error handling and resilience mechanisms across Echolon AI, enabling graceful degradation, automatic recovery, and reliable user experiences.

## Completed Components

### 1. Backend Exception Hierarchy (exceptions.py - 236 lines)

**Purpose**: Structured exception hierarchy for all error types

**Classes Implemented**:
- `ErrorResponse`: Standard error response Pydantic model
- `EcholonException`: Base exception with HTTP status mapping
- `AuthenticationError`: 401 Unauthorized
- `AuthorizationError`: 403 Forbidden
- `ValidationError`: 422 Unprocessable Entity
- `DatabaseError`: 500 Internal Server Error
- `DataSourceError`: 503 Service Unavailable (with retry-after)
- `APIIntegrationError`: 503 Service Unavailable (with retry-after)
- `RateLimitError`: 429 Too Many Requests
- `ResourceNotFoundError`: 404 Not Found
- `TimeoutError`: 504 Gateway Timeout
- `CircuitBreakerOpenError`: 503 Service Unavailable
- `StreamlitSessionError`: 400 Bad Request
- `DataProcessingError`: 500 Internal Server Error
- `ConfigurationError`: 500 Internal Server Error

**Key Features**:
- Automatic HTTP status code mapping
- Retry-after header support for transient failures
- Request ID tracking throughout response
- Timestamp recording for audit logs
- Conversion methods to FastAPI HTTPException

### 2. Retry Logic & Circuit Breaker (retry_logic.py - 331 lines)

**Purpose**: Resilient failure handling with automatic recovery

**Classes Implemented**:
- `CircuitState`: Enum for CLOSED/OPEN/HALF_OPEN states
- `CircuitBreaker`: Production-grade circuit breaker
  - Failure threshold tracking
  - Automatic state transitions
  - Recovery timeout management
  - Status reporting
  
- `RetryStrategy`: Configurable retry with exponential backoff
  - Max attempt configuration
  - Base/max delay settings
  - Jitter to prevent thundering herd
  - Selective exception handling
  
- `RetryManager`: Centralized registry for all retry/CB configurations

**Decorators**:
- `@with_retry`: Function decorator for automatic retries

**Key Features**:
- Exponential backoff formula: base * (2^(attempt-1))
- Jitter: ±20% randomization to prevent synchronized retries
- Circuit breaker state machine:
  - CLOSED: Normal operation
  - OPEN: Reject requests after threshold failures
  - HALF_OPEN: Attempt recovery after timeout
- Automatic transition to HALF_OPEN after recovery_timeout
- Success on HALF_OPEN returns to CLOSED
- Failure on HALF_OPEN returns to OPEN

### 3. Error Handling Middleware (error_handling.py - 283 lines)

**Purpose**: Global error handling for FastAPI application

**Middleware Classes**:
- `RequestIDMiddleware`: Add X-Request-ID to all requests/responses
- `ErrorHandlingMiddleware`: Global error handling with logging

**Exception Handlers**:
- `echolon_exception_handler`: Handle custom Echolon exceptions
- `validation_exception_handler`: Handle Pydantic validation errors
- `general_exception_handler`: Catch-all for unexpected errors

**Utilities**:
- `ErrorHandler`: Static utility methods for error operations
  - `get_error_code()`: Extract error code from exception
  - `format_error_response()`: Standardize error response format
  - `should_retry()`: Determine if error is retryable
  - `with_error_handling()`: Decorator for function error handling

**Setup Function**:
- `setup_error_handling(app)`: One-line initialization for FastAPI apps

**Key Features**:
- Request-scoped error tracking via X-Request-ID header
- Automatic error logging at appropriate levels
- Structured error responses with request context
- Support for both sync and async decorators
- Fallback value support for failed functions
- Per-request error context isolation

## Error Handling Flow

```
Request
  |
  v
RequestIDMiddleware (Add X-Request-ID)
  |
  v
ErrorHandlingMiddleware (Try/catch with logging)
  |
  v
Route Handler
  |
  +---> Raises EcholonException
  |       |
  |       v
  |    Exception Handler
  |       |
  |       v
  |    ErrorResponse (with request_id, timestamp)
  |       |
  |       v
  |    HTTP Response (status_code + body)
  |
  +---> Returns normally
         |
         v
      HTTP Response
```

## Retryable Status Codes

The following status codes are automatically considered retryable:
- **408**: Request Timeout
- **429**: Too Many Requests (with Retry-After header)
- **500**: Internal Server Error
- **502**: Bad Gateway
- **503**: Service Unavailable (with Retry-After header)
- **504**: Gateway Timeout

## Usage Examples

### Using Custom Exceptions

```python
from exceptions import DataSourceError, ValidationError

# Raise with retry-after
raise DataSourceError(
    message="Stripe API unavailable",
    detail="The Stripe API is temporarily unavailable",
    retry_after=60
)

# Raise validation error
raise ValidationError(
    message="Invalid email format",
    detail="Must be a valid email address"
)
```

### Using Circuit Breaker

```python
from retry_logic import retry_manager

# Register circuit breaker
retry_manager.register_circuit_breaker(
    name="stripe",
    failure_threshold=5,
    recovery_timeout=60
)

# Use in code
breaker = retry_manager.get_circuit_breaker("stripe")
try:
    result = breaker.call(call_stripe_api)
except CircuitBreakerOpenError as e:
    logger.error(f"Stripe API is unavailable: {e}")
    # Serve stale data or graceful degradation
```

### Using Retry Decorator

```python
from retry_logic import with_retry
from exceptions import APIIntegrationError

@with_retry(
    max_attempts=3,
    base_delay=1.0,
    max_delay=10.0,
    exception_types=(APIIntegrationError,)
)
def fetch_stripe_data(customer_id):
    # Will retry up to 3 times with exponential backoff
    return stripe.Customer.retrieve(customer_id)
```

### Using Error Handling Decorator

```python
from error_handling import with_error_handling

@with_error_handling(
    fallback_value={"status": "unknown"},
    log_level="warning"
)
def get_cache_value(key):
    # Returns fallback value if exception occurs
    return redis.get(key)
```

### Setting Up in FastAPI

```python
from fastapi import FastAPI
from error_handling import setup_error_handling

app = FastAPI()
setup_error_handling(app)  # One line!
```

## Integration Checklist

- [ ] **Backend/main.py**: Import and call `setup_error_handling(app)`
- [ ] **Backend routes**: Replace bare exceptions with `EcholonException` subclasses
- [ ] **Database operations**: Wrap with `@with_error_handling` or catch `DatabaseError`
- [ ] **API calls**: Use `@with_retry` or `CircuitBreaker` for external APIs
- [ ] **Dashboard pages**: Implement error UI components (next step)
- [ ] **Logging**: Configure logging handlers and levels

## Resilience Patterns Implemented

### 1. Exponential Backoff with Jitter
- Prevents retry storms
- Gradually increases wait time
- ±20% jitter spreads retry timing

### 2. Circuit Breaker Pattern
- Fails fast when service is down
- Prevents cascading failures
- Automatic recovery after timeout
- HALF_OPEN state for safe recovery testing

### 3. Request ID Tracking
- Unique ID per request
- Propagated through all errors
- Enables error correlation in logs

### 4. Structured Error Responses
- Machine-readable error codes
- Human-readable messages
- Contextual details for debugging
- Timestamp for audit trails

## Performance Characteristics

| Component | Operation | Time Complexity | Space Complexity |
|-----------|-----------|-----------------|------------------|
| CircuitBreaker | call() | O(1) | O(1) |
| RetryStrategy | execute() | O(n) where n=attempts | O(1) |
| ErrorMiddleware | dispatch() | O(1) | O(1) |
| Exception Handler | handle() | O(1) | O(1) |

## Testing Recommendations

### Unit Tests
- Test each exception type's status code and message format
- Verify circuit breaker state transitions
- Test retry exponential backoff calculation
- Verify jitter range (±20%)

### Integration Tests
- Test middleware adds X-Request-ID header
- Verify error responses have correct structure
- Test exception handler catches all exception types
- Verify retry decorator works with async/sync functions

### Load Tests
- Test circuit breaker prevents cascading failures
- Verify exponential backoff prevents thundering herd
- Test request ID generation performance
- Verify middleware overhead is minimal

## Next Steps

1. **Streamlit Error UI** (error_handler.py)
   - Error message display component
   - Retry button with exponential backoff
   - Error details expandable section
   - Request ID display for support

2. **Logging Integration**
   - Configure structured JSON logging
   - Error tracking service integration (Sentry)
   - Log aggregation setup

3. **Monitoring Dashboard**
   - Circuit breaker status visualization
   - Error rate tracking
   - Retry success rates
   - Response time distributions

4. **Documentation**
   - Runbook for common errors
   - Troubleshooting guide
   - Error code reference

## Statistics

**Lines of Code**:
- exceptions.py: 236 lines
- retry_logic.py: 331 lines
- error_handling.py: 283 lines
- Total: 850 lines of production-grade error handling

**Coverage**:
- 12 custom exception types
- 3-state circuit breaker pattern
- Exponential backoff with jitter
- Global exception handlers for FastAPI
- Request ID tracking
- Retry decorator support

**Features Enabled**:
- ✅ Graceful degradation on API failures
- ✅ Automatic retry with exponential backoff
- ✅ Circuit breaker prevents cascading failures
- ✅ Structured error responses
- ✅ Request tracking for debugging
- ✅ Retry-after header support
- ✅ Configurable resilience patterns
- ✅ Both sync and async support

## Success Metrics

After Phase 9 implementation:
1. **Availability**: Graceful handling of transient failures
2. **Reliability**: Automatic recovery from temporary outages
3. **Observability**: Complete error tracking with request IDs
4. **Debuggability**: Structured errors with context
5. **Resilience**: Circuit breaker prevents cascading failures
