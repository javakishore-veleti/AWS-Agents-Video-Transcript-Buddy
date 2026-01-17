"""
Transcript Routes - REST endpoints for transcript management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from typing import List, Optional, Dict, Any

from services.transcript_service import TranscriptService
from api.models.request_models import ReindexRequest
from api.models.response_models import (
    TranscriptResponse,
    TranscriptListResponse,
    UploadResponse,
    DeleteResponse,
    ReindexResponse
)
from common.exceptions import (
    TranscriptNotFoundException,
    ValidationException,
    S3ConnectionException
)

router = APIRouter()

# Initialize service
transcript_service = TranscriptService()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a transcript",
    description="Upload a transcript file (.txt, .srt, .vtt, .json)"
)
async def upload_transcript(
    file: UploadFile = File(..., description="Transcript file to upload"),
    auto_index: bool = Query(True, description="Automatically index in vector store")
) -> UploadResponse:
    """
    Upload a transcript file.
    
    - **file**: Transcript file (.txt, .srt, .vtt, .json)
    - **auto_index**: Whether to automatically index for searching (default: True)
    """
    try:
        content = await file.read()
        
        result = await transcript_service.upload_transcript(
            filename=file.filename,
            content=content,
            auto_index=auto_index
        )
        
        return UploadResponse(
            success=True,
            message=f"Transcript '{file.filename}' uploaded successfully",
            data=result
        )
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    
    except S3ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.get(
    "/",
    response_model=TranscriptListResponse,
    summary="List all transcripts",
    description="Get a list of all uploaded transcripts"
)
async def list_transcripts() -> TranscriptListResponse:
    """
    List all transcripts with their indexing status.
    """
    try:
        transcripts = await transcript_service.list_transcripts()
        
        return TranscriptListResponse(
            success=True,
            message=f"Found {len(transcripts)} transcripts",
            data=transcripts,
            total=len(transcripts)
        )
    
    except S3ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.get(
    "/{filename}",
    response_model=TranscriptResponse,
    summary="Get a transcript",
    description="Get transcript content and metadata"
)
async def get_transcript(filename: str) -> TranscriptResponse:
    """
    Get a specific transcript by filename.
    
    - **filename**: Name of the transcript file
    """
    try:
        transcript = await transcript_service.get_transcript(filename)
        
        return TranscriptResponse(
            success=True,
            message=f"Transcript '{filename}' retrieved successfully",
            data=transcript
        )
    
    except TranscriptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    
    except S3ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.delete(
    "/{filename}",
    response_model=DeleteResponse,
    summary="Delete a transcript",
    description="Delete a transcript from S3 and vector store"
)
async def delete_transcript(filename: str) -> DeleteResponse:
    """
    Delete a specific transcript.
    
    - **filename**: Name of the transcript file to delete
    """
    try:
        # Check if exists first
        exists = await transcript_service.transcript_exists(filename)
        if not exists:
            raise TranscriptNotFoundException(filename)
        
        result = await transcript_service.delete_transcript(filename)
        
        return DeleteResponse(
            success=result,
            message=f"Transcript '{filename}' deleted successfully" if result else f"Failed to delete '{filename}'",
            filename=filename
        )
    
    except TranscriptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    
    except S3ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.post(
    "/{filename}/reindex",
    response_model=ReindexResponse,
    summary="Reindex a transcript",
    description="Reindex a transcript in the vector store"
)
async def reindex_transcript(filename: str) -> ReindexResponse:
    """
    Reindex a specific transcript in the vector store.
    
    - **filename**: Name of the transcript file to reindex
    """
    try:
        result = await transcript_service.reindex_transcript(filename)
        
        return ReindexResponse(
            success=True,
            message=f"Transcript '{filename}' reindexed successfully",
            data=result
        )
    
    except TranscriptNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    
    except S3ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.post(
    "/reindex-all",
    response_model=ReindexResponse,
    summary="Reindex all transcripts",
    description="Reindex all transcripts in the vector store"
)
async def reindex_all_transcripts() -> ReindexResponse:
    """
    Reindex all transcripts in the vector store.
    """
    try:
        result = await transcript_service.reindex_all_transcripts()
        
        return ReindexResponse(
            success=True,
            message=f"Reindexed {result['success']} of {result['total']} transcripts",
            data=result
        )
    
    except S3ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.head(
    "/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Check if transcript exists",
    description="Check if a transcript exists without downloading content"
)
async def check_transcript_exists(filename: str):
    """
    Check if a transcript exists.
    
    - **filename**: Name of the transcript file
    
    Returns 200 if exists, 404 if not.
    """
    exists = await transcript_service.transcript_exists(filename)
    
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Transcript '{filename}' not found"}
        )
    
    return None