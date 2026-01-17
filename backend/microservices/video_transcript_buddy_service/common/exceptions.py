"""
Custom Exceptions for Video Transcript Buddy Service.

All application-specific exceptions inherit from BaseAppException.
"""

from typing import Optional


class BaseAppException(Exception):
    """Base exception for all application exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class TranscriptNotFoundException(BaseAppException):
    """Raised when a transcript is not found."""
    
    def __init__(self, transcript_name: str):
        super().__init__(
            message=f"Transcript not found: {transcript_name}",
            error_code="TRANSCRIPT_NOT_FOUND",
            details={"transcript_name": transcript_name}
        )


class S3ConnectionException(BaseAppException):
    """Raised when S3 connection fails."""
    
    def __init__(self, message: str, bucket: Optional[str] = None):
        super().__init__(
            message=f"S3 connection error: {message}",
            error_code="S3_CONNECTION_ERROR",
            details={"bucket": bucket} if bucket else {}
        )


class VectorStoreException(BaseAppException):
    """Raised when vector store operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=f"Vector store error: {message}",
            error_code="VECTOR_STORE_ERROR",
            details={"operation": operation} if operation else {}
        )


class AgentException(BaseAppException):
    """Raised when agent operations fail."""
    
    def __init__(self, message: str, agent_name: Optional[str] = None):
        super().__init__(
            message=f"Agent error: {message}",
            error_code="AGENT_ERROR",
            details={"agent_name": agent_name} if agent_name else {}
        )


class ValidationException(BaseAppException):
    """Raised when validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=f"Validation error: {message}",
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {}
        )


class ConfigurationException(BaseAppException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=f"Configuration error: {message}",
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key} if config_key else {}
        )


class AuthenticationException(BaseAppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR"
        )


class RateLimitException(BaseAppException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after} if retry_after else {}
        )