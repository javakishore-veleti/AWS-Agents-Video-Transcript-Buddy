"""
Query Routes - REST endpoints for querying transcripts.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from config.database import get_db
from services.query_service import QueryService
from services.usage_service import UsageService
from api.models.request_models import QueryRequest, SearchRequest
from api.models.response_models import (
    QueryResponse,
    SearchResponse,
    SuggestionsResponse
)
from api.dependencies.auth import get_current_user, check_query_limit
from api.dependencies.id_encryption import get_id_encryptor
from utils.id_encryption import UserIDEncryptor
from models.user import User
from models.transcript import Transcript
from common.exceptions import (
    ValidationException,
    AgentException,
    VectorStoreException
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service
query_service = QueryService()


def _resolve_transcript_ids_to_filenames(
    transcript_ids: Optional[List[str]],
    encryptor: UserIDEncryptor,
    current_user: User,
    db: Session
) -> Optional[List[str]]:
    """
    Resolve encrypted transcript IDs to filenames for vector store search.
    
    The frontend sends encrypted database UUIDs (transcript.id), but the vector
    store indexes documents by filename. This function:
    1. Decrypts the encrypted IDs to get the actual UUIDs
    2. Looks up transcripts in the database
    3. Returns the corresponding filenames
    
    Args:
        transcript_ids: List of encrypted transcript IDs from frontend
        encryptor: User-specific ID encryptor
        current_user: The authenticated user
        db: Database session
        
    Returns:
        List of filenames for vector store search, or None if no IDs provided
    """
    if not transcript_ids:
        return None
    
    filenames = []
    for encrypted_id in transcript_ids:
        try:
            # Decrypt the ID to get the actual database UUID
            decrypted_id = encryptor.decrypt(encrypted_id)
            logger.debug(f"Decrypted transcript ID: {encrypted_id} -> {decrypted_id}")
            
            # Look up the transcript to get the filename
            transcript = db.query(Transcript).filter(
                Transcript.id == decrypted_id,
                Transcript.user_id == current_user.id
            ).first()
            
            if transcript:
                filenames.append(transcript.filename)
                logger.debug(f"Resolved transcript {decrypted_id} to filename: {transcript.filename}")
            else:
                logger.warning(f"Transcript not found for ID: {decrypted_id}")
        
        except Exception as e:
            logger.warning(f"Failed to decrypt/resolve transcript ID {encrypted_id}: {e}")
            # Skip invalid IDs silently - they might be stale encrypted IDs
            continue
    
    if not filenames:
        logger.warning("No valid transcript filenames resolved - search may return empty results")
        return None
    
    logger.info(f"Resolved {len(transcript_ids)} encrypted IDs to {len(filenames)} filenames: {filenames}")
    return filenames


@router.post(
    "/",
    response_model=QueryResponse,
    summary="Query transcripts",
    description="Ask a question and get an answer based on transcript content"
)
async def query_transcripts(
    request: QueryRequest,
    current_user: User = Depends(check_query_limit),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
) -> QueryResponse:
    """
    Process a user query against transcripts.
    
    - **question**: The question to ask
    - **transcript_ids**: Optional list of encrypted transcript IDs to search within
    - **max_results**: Maximum number of source chunks to consider (default: 5)
    - **llm_provider**: Optional LLM provider (openai, ollama, lmstudio)
    - **llm_model**: Optional model name
    - **llm_temperature**: Optional temperature (0-1)
    """
    try:
        # CRITICAL: Convert encrypted transcript IDs to filenames for vector store search
        # Frontend sends encrypted UUIDs (transcript.id), but vector store indexes by filename
        resolved_filenames = _resolve_transcript_ids_to_filenames(
            request.transcript_ids,
            encryptor,
            current_user,
            db
        )
        
        logger.info(f"Query: '{request.question[:50]}...' by user={current_user.id} on {len(resolved_filenames or [])} transcripts")
        
        result = await query_service.query(
            question=request.question,
            transcript_ids=resolved_filenames,  # Pass filenames, not encrypted IDs
            user_id=current_user.id,  # CRITICAL: Multi-tenancy - only search user's data
            max_results=request.max_results,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model,
            llm_temperature=request.llm_temperature
        )
        
        # Determine if complex query (based on length or keywords)
        is_complex = len(request.question) > 100 or any(
            word in request.question.lower() 
            for word in ["compare", "analyze", "summarize", "explain", "relationship"]
        )
        
        # Determine model used for usage tracking
        model_used = request.llm_model or "gpt-4"
        
        # Record usage
        usage_service = UsageService(db)
        usage_service.record_query(
            user_id=current_user.id,
            is_complex=is_complex,
            model_used=model_used
        )
        
        return QueryResponse(
            success=True,
            message="Query processed successfully",
            data=result
        )
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    
    except AgentException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )
    
    except VectorStoreException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Search transcripts",
    description="Search for relevant transcript chunks without generating an answer"
)
async def search_transcripts(
    request: SearchRequest,
    current_user: User = Depends(check_query_limit),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
) -> SearchResponse:
    """
    Search for relevant transcript chunks.
    
    - **query**: The search query
    - **transcript_ids**: Optional list of encrypted transcript IDs to search within
    - **max_results**: Maximum number of results (default: 5)
    """
    try:
        # Convert encrypted transcript IDs to filenames for vector store search
        resolved_filenames = _resolve_transcript_ids_to_filenames(
            request.transcript_ids,
            encryptor,
            current_user,
            db
        )
        
        results = await query_service.search(
            query=request.query,
            transcript_ids=resolved_filenames,  # Pass filenames, not encrypted IDs
            user_id=current_user.id,  # CRITICAL: Multi-tenancy - only search user's data
            max_results=request.max_results
        )
        
        # Record as simple query
        usage_service = UsageService(db)
        usage_service.record_query(
            user_id=current_user.id,
            is_complex=False,
            model_used=None
        )
        
        return SearchResponse(
            success=True,
            message=f"Found {len(results)} matching chunks",
            data=results,
            total=len(results)
        )
    
    except VectorStoreException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.to_dict()
        )


@router.post(
    "/validate",
    summary="Validate a query",
    description="Validate a query before processing"
)
async def validate_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate a user query before processing.
    
    - **question**: The question to validate
    """
    result = await query_service.validate_query(request.question)
    
    if not result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": True,
                "error_code": "VALIDATION_ERROR",
                "message": result["message"]
            }
        )
    
    return {
        "success": True,
        "message": "Query is valid",
        "data": result
    }


@router.get(
    "/suggestions",
    response_model=SuggestionsResponse,
    summary="Get suggested questions",
    description="Get suggested questions based on transcript content"
)
async def get_suggestions(
    transcript_ids: Optional[List[str]] = None,
    count: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
) -> SuggestionsResponse:
    """
    Get suggested questions based on transcript content.
    
    - **transcript_ids**: Optional list of encrypted transcript IDs to base suggestions on
    - **count**: Number of suggestions to return (default: 5)
    """
    try:
        # Convert encrypted transcript IDs to filenames
        resolved_filenames = _resolve_transcript_ids_to_filenames(
            transcript_ids,
            encryptor,
            current_user,
            db
        )
        
        suggestions = await query_service.get_suggested_questions(
            transcript_ids=resolved_filenames,  # Pass filenames, not encrypted IDs
            count=count
        )
        
        return SuggestionsResponse(
            success=True,
            message=f"Generated {len(suggestions)} suggestions",
            data=suggestions
        )
    
    except Exception as e:
        # Return default suggestions on error
        return SuggestionsResponse(
            success=True,
            message="Using default suggestions",
            data=[
                "What are the main topics discussed?",
                "Can you summarize the key points?",
                "What are the most important takeaways?"
            ]
        )