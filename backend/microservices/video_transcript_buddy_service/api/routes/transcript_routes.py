"""
Transcript Routes - REST endpoints for transcript management.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, Depends
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from config.database import get_db
from services.transcript_service_v2 import TranscriptServiceV2
from services.usage_service import UsageService
from api.models.request_models import ReindexRequest
from api.models.response_models import (
    TranscriptResponse,
    TranscriptListResponse,
    UploadResponse,
    DeleteResponse,
    ReindexResponse
)
from api.dependencies.auth import get_current_user, check_upload_limit
from models.user import User
from models.conversation import Conversation
from models.subscription import get_tier_limits
from api.dependencies.id_encryption import get_id_encryptor
from utils.id_encryption import UserIDEncryptor
from common.exceptions import (
    TranscriptNotFoundException,
    ValidationException,
    S3ConnectionException
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service
transcript_service = TranscriptServiceV2()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a transcript",
    description="Upload a transcript file (.txt, .srt, .vtt, .json)"
)
async def upload_transcript(
    file: UploadFile = File(..., description="Transcript file to upload"),
    auto_index: bool = Query(True, description="Automatically index in vector store"),
    conversation_id: str = Query(..., description="Encrypted conversation ID to associate with transcript"),
    current_user: User = Depends(check_upload_limit),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
) -> UploadResponse:
    """
    Upload a transcript file.
    
    - **file**: Transcript file (.txt, .srt, .vtt, .json)
    - **auto_index**: Whether to automatically index for searching (default: True)
    - **conversation_id**: Encrypted ID of the conversation to associate with the transcript
    """
    try:
        # Decrypt the conversation ID
        try:
            decrypted_conversation_id = encryptor.decrypt(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired conversation ID"
            )
        
        # SECURITY: Verify conversation belongs to current user
        conversation = db.query(Conversation).filter(
            Conversation.id == decrypted_conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conversation not found or access denied"
            )
        
        content = await file.read()
        
        # Check file size limit for tier
        tier_limits = get_tier_limits(current_user.tier)
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > tier_limits.max_file_size_mb:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds limit for {current_user.tier} tier"
            )
        
        # Upload transcript
        result = await transcript_service.upload_transcript(
            filename=file.filename,
            content=content,
            user_id=current_user.id,
            conversation_id=decrypted_conversation_id,  # Use decrypted ID
            db=db,
            auto_index=auto_index
        )
        
        # Record usage
        usage_service = UsageService(db)
        usage_service.record_upload(
            user_id=current_user.id,
            filename=file.filename,
            file_size_bytes=len(content)
        )
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {file.filename}",
            data=result
        )
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=TranscriptListResponse,
    summary="List all transcripts",
    description="Get a list of all uploaded transcripts"
)
async def list_transcripts(
    conversation_id: Optional[str] = Query(None, description="Optional: Encrypted conversation ID to filter by"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
) -> TranscriptListResponse:
    """
    List all transcripts with their indexing status.
    Optionally filter by conversation_id.
    """
    try:
        # Decrypt conversation_id if provided for filtering
        decrypted_conv_id = None
        if conversation_id:
            try:
                decrypted_conv_id = encryptor.decrypt(conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired conversation ID"
                )
        
        transcripts = await transcript_service.list_transcripts(
            db, 
            user_id=current_user.id,
            conversation_id=decrypted_conv_id
        )
        
        # Encrypt conversation_id in each transcript
        encrypted_transcripts = []
        for t in transcripts:
            t_dict = dict(t) if isinstance(t, dict) else t
            if 'conversation_id' in t_dict and t_dict['conversation_id'] is not None:
                t_dict['conversation_id'] = encryptor.encrypt(t_dict['conversation_id'])
            encrypted_transcripts.append(t_dict)
        
        return TranscriptListResponse(
            success=True,
            message=f"Found {len(transcripts)} transcripts",
            data=encrypted_transcripts,
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
async def get_transcript(
    filename: str,
    current_user: User = Depends(get_current_user)
) -> TranscriptResponse:
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
async def delete_transcript(
    filename: str,
    current_user: User = Depends(get_current_user)
) -> DeleteResponse:
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
async def reindex_transcript(
    filename: str,
    current_user: User = Depends(get_current_user)
) -> ReindexResponse:
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
async def reindex_all_transcripts(
    current_user: User = Depends(get_current_user)
) -> ReindexResponse:
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
async def check_transcript_exists(
    filename: str,
    current_user: User = Depends(get_current_user)
):
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