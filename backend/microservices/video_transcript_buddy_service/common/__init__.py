"""Common module - shared exceptions and constants."""

from .exceptions import (
    BaseAppException,
    TranscriptNotFoundException,
    S3ConnectionException,
    VectorStoreException,
    AgentException,
    ValidationException,
)
from .constants import (
    SUPPORTED_FILE_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)

__all__ = [
    # Exceptions
    "BaseAppException",
    "TranscriptNotFoundException",
    "S3ConnectionException",
    "VectorStoreException",
    "AgentException",
    "ValidationException",
    # Constants
    "SUPPORTED_FILE_EXTENSIONS",
    "MAX_FILE_SIZE_MB",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
]