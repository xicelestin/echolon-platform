"""Retry logic and circuit breaker implementation.

Provides resilient mechanisms for handling transient failures:
- Exponential backoff with jitter
- Configurable retry strategies
- Circuit breaker pattern
- Timeout management
- Graceful degradation
"""

import time
import random
import logging
from typing import Callable, TypeVar, Optional, Any
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum
from exceptions import (
    EcholonException,
    TimeoutError as EcholonTimeoutError,
    CircuitBreakerOpenError,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"           # Normal operation
    OPEN = "open"               # Failing, reject requests
    HALF_OPEN = "half_open"     # Recovery attempt


class CircuitBreaker:
    """Circuit breaker implementation for resilient API calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exceptions: tuple = (Exception,),
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            expected_exceptions: Exception types to count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.opened_at = None
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
            else:
                raise CircuitBreakerOpenError(
                    service_name=func.__name__,
                    retry_after=self._retry_after(),
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exceptions as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.success_count = 0
            logger.info("Circuit breaker closed (recovered)")
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.utcnow()
            logger.warning(
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if recovery timeout has elapsed."""
        if not self.opened_at:
            return False
        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _retry_after(self) -> int:
        """Calculate retry-after header value."""
        if not self.opened_at:
            return self.recovery_timeout
        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        remaining = max(0, int(self.recovery_timeout - elapsed))
        return remaining or self.recovery_timeout
    
    def reset(self):
        """Manually reset circuit breaker."""
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.opened_at = None
        logger.info("Circuit breaker manually reset")
    
    def get_status(self) -> dict:
        """Get circuit breaker status."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


class RetryStrategy:
    """Configurable retry strategy with exponential backoff."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry strategy.
        
        Args:
            max_attempts: Maximum number of attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay between retries
            exponential_base: Exponential backoff multiplier
            jitter: Add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def execute(
        self,
        func: Callable[..., T],
        *args,
        exception_types: tuple = (Exception,),
        **kwargs,
    ) -> T:
        """Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            exception_types: Exceptions to retry on
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                last_exception = e
                
                if attempt == self.max_attempts:
                    logger.error(
                        f"All {self.max_attempts} retry attempts failed for {func.__name__}",
                        exc_info=e,
                    )
                    raise
                
                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Retry attempt {attempt}/{self.max_attempts} for {func.__name__} "
                    f"after {delay:.2f}s: {str(e)}"
                )
                time.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff.
        
        Args:
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: base * (exponential_base ^ (attempt - 1))
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        
        # Cap at max delay
        delay = min(delay, self.max_delay)
        
        # Add jitter (±20%)
        if self.jitter:
            jitter_amount = delay * 0.2
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # Ensure non-negative
        
        return delay


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exception_types: tuple = (Exception,),
):
    """Decorator for retrying function calls.
    
    Args:
        max_attempts: Maximum retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        exception_types: Exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        strategy = RetryStrategy(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return strategy.execute(
                func,
                *args,
                exception_types=exception_types,
                **kwargs,
            )
        
        return wrapper
    
    return decorator


class RetryManager:
    """Central manager for retry strategies and circuit breakers."""
    
    def __init__(self):
        """Initialize retry manager."""
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_strategies: dict[str, RetryStrategy] = {}
    
    def register_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ):
        """Register a circuit breaker."""
        self.circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
        logger.info(f"Registered circuit breaker: {name}")
    
    def register_retry_strategy(
        self,
        name: str,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ):
        """Register a retry strategy."""
        self.retry_strategies[name] = RetryStrategy(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
        )
        logger.info(f"Registered retry strategy: {name}")
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self.circuit_breakers.get(name)
    
    def get_retry_strategy(self, name: str) -> Optional[RetryStrategy]:
        """Get retry strategy by name."""
        return self.retry_strategies.get(name)
    
    def get_status(self) -> dict:
        """Get status of all circuit breakers."""
        return {
            "circuit_breakers": {
                name: cb.get_status()
                for name, cb in self.circuit_breakers.items()
            }
        }


# Global retry manager instance
retry_manager = RetryManager()
