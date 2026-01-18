"""
Response Models - Pydantic models for API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Import auth models
from .auth_response_models import AuthResponse, TokenResponse, UserResponse


class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    
    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )
    
    message: str = Field(
        ...,
        description="Human-readable message about the result"
    )


class TranscriptData(BaseModel):
    """Transcript data model."""
    
    filename: str = Field(..., description="Name of the transcript file")
    key: Optional[str] = Field(None, description="S3 object key")
    content: Optional[str] = Field(None, description="Transcript content")
    size: Optional[int] = Field(None, description="File size in bytes")
    size_formatted: Optional[str] = Field(None, description="Human-readable file size")
    last_modified: Optional[str] = Field(None, description="Last modified timestamp")
    indexed: Optional[bool] = Field(None, description="Whether indexed in vector store")
    chunk_count: Optional[int] = Field(None, description="Number of chunks in vector store")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TranscriptResponse(BaseResponse):
    """Response model for single transcript operations."""
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Transcript data"
    )


class TranscriptListResponse(BaseResponse):
    """Response model for listing transcripts."""
    
    data: List[Dict[str, Any]] = Field(
        default=[],
        description="List of transcripts"
    )
    
    total: int = Field(
        default=0,
        description="Total number of transcripts"
    )


class UploadResponse(BaseResponse):
    """Response model for transcript upload."""
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Upload result details"
    )


class DeleteResponse(BaseResponse):
    """Response model for transcript deletion."""
    
    filename: str = Field(
        ...,
        description="Name of the deleted file"
    )


class ReindexResponse(BaseResponse):
    """Response model for reindex operations."""
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Reindex result details"
    )


class QueryResultData(BaseModel):
    """Query result data model."""
    
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source references")
    confidence: float = Field(default=0.0, description="Confidence score (0-1)")
    chunks_used: Optional[int] = Field(None, description="Number of chunks used")


class QueryResponse(BaseResponse):
    """Response model for query operations."""
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Query result with answer and sources"
    )


class SearchResultItem(BaseModel):
    """Individual search result item."""
    
    id: str = Field(..., description="Chunk ID")
    content: str = Field(..., description="Chunk content")
    metadata: Dict[str, Any] = Field(default={}, description="Chunk metadata")
    score: float = Field(..., description="Similarity score")
    distance: Optional[float] = Field(None, description="Vector distance")


class SearchResponse(BaseResponse):
    """Response model for search operations."""
    
    data: List[Dict[str, Any]] = Field(
        default=[],
        description="Search results"
    )
    
    total: int = Field(
        default=0,
        description="Total number of results"
    )


class SuggestionsResponse(BaseResponse):
    """Response model for suggested questions."""
    
    data: List[str] = Field(
        default=[],
        description="List of suggested questions"
    )


class ErrorDetail(BaseModel):
    """Error detail model."""
    
    error: bool = Field(default=True)
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Health status")
    service: Optional[str] = Field(None, description="Service name")
    version: Optional[str] = Field(None, description="Service version")
    timestamp: str = Field(..., description="Check timestamp")
    checks: Optional[Dict[str, bool]] = Field(None, description="Individual check results")


class VectorStoreStatsResponse(BaseResponse):
    """Response model for vector store statistics."""
    
    data: Dict[str, Any] = Field(
        default={},
        description="Vector store statistics"
    )


# Export all
__all__ = [
    "BaseResponse",
    "TranscriptData",
    "TranscriptResponse",
    "TranscriptListResponse",
    "UploadResponse",
    "DeleteResponse",
    "ReindexResponse",
    "QueryResultData",
    "QueryResponse",
    "SearchResultItem",
    "SearchResponse",
    "SuggestionsResponse",
    "ErrorDetail",
    "HealthCheckResponse",
    "VectorStoreStatsResponse",
    "AuthResponse",
    "TokenResponse",
    "UserResponse",
]