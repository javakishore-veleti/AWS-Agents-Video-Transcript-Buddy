"""
Request Models - Pydantic models for API request validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

# Import auth models
from .auth_request_models import RegisterRequest, LoginRequest, RefreshTokenRequest


class QueryRequest(BaseModel):
    """Request model for querying transcripts."""
    
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The question to ask about the transcripts",
        examples=["What are the main topics discussed?"]
    )
    
    transcript_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of transcript filenames to search within. If not provided, searches all transcripts.",
        examples=[["video1.txt", "video2.txt"]]
    )
    
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of source chunks to consider for answering"
    )
    
    # LLM settings - optional, will use defaults if not provided
    llm_provider: Optional[str] = Field(
        default=None,
        description="LLM provider: openai, ollama, or lmstudio"
    )
    
    llm_model: Optional[str] = Field(
        default=None,
        description="Model name to use for the LLM"
    )
    
    llm_temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Temperature for LLM responses (0-1)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the main topics discussed in the video?",
                "transcript_ids": None,
                "max_results": 5,
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "llm_temperature": 0.7
            }
        }


class SearchRequest(BaseModel):
    """Request model for searching transcripts."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The search query",
        examples=["machine learning"]
    )
    
    transcript_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of transcript filenames to search within",
        examples=[["video1.txt", "video2.txt"]]
    )
    
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results to return"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning algorithms",
                "transcript_ids": None,
                "max_results": 5
            }
        }


class ReindexRequest(BaseModel):
    """Request model for reindexing transcripts."""
    
    chunk_size: Optional[int] = Field(
        default=None,
        ge=100,
        le=5000,
        description="Size of text chunks for indexing (default: 1000)"
    )
    
    chunk_overlap: Optional[int] = Field(
        default=None,
        ge=0,
        le=500,
        description="Overlap between chunks (default: 200)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_size": 1000,
                "chunk_overlap": 200
            }
        }


class TranscriptUploadRequest(BaseModel):
    """Request model for transcript upload metadata."""
    
    auto_index: bool = Field(
        default=True,
        description="Whether to automatically index the transcript in vector store"
    )
    
    tags: Optional[List[str]] = Field(
        default=None,
        description="Optional tags for the transcript",
        examples=[["tutorial", "python", "beginner"]]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "auto_index": True,
                "tags": ["tutorial", "python"]
            }
        }


# Export all
__all__ = [
    "QueryRequest",
    "SearchRequest",
    "ReindexRequest",
    "TranscriptUploadRequest",
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
]