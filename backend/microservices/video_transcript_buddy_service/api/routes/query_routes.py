"""
Query Routes - REST endpoints for querying transcripts.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from services.query_service import QueryService
from api.models.request_models import QueryRequest, SearchRequest
from api.models.response_models import (
    QueryResponse,
    SearchResponse,
    SuggestionsResponse
)
from common.exceptions import (
    ValidationException,
    AgentException,
    VectorStoreException
)

router = APIRouter()

# Initialize service
query_service = QueryService()


@router.post(
    "/",
    response_model=QueryResponse,
    summary="Query transcripts",
    description="Ask a question and get an answer based on transcript content"
)
async def query_transcripts(request: QueryRequest) -> QueryResponse:
    """
    Process a user query against transcripts.
    
    - **question**: The question to ask
    - **transcript_ids**: Optional list of transcript filenames to search within
    - **max_results**: Maximum number of source chunks to consider (default: 5)
    """
    try:
        result = await query_service.query(
            question=request.question,
            transcript_ids=request.transcript_ids,
            max_results=request.max_results
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
async def search_transcripts(request: SearchRequest) -> SearchResponse:
    """
    Search for relevant transcript chunks.
    
    - **query**: The search query
    - **transcript_ids**: Optional list of transcript filenames to search within
    - **max_results**: Maximum number of results (default: 5)
    """
    try:
        results = await query_service.search(
            query=request.query,
            transcript_ids=request.transcript_ids,
            max_results=request.max_results
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
async def validate_query(request: QueryRequest):
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
    count: int = 5
) -> SuggestionsResponse:
    """
    Get suggested questions based on transcript content.
    
    - **transcript_ids**: Optional list of transcript filenames to base suggestions on
    - **count**: Number of suggestions to return (default: 5)
    """
    try:
        suggestions = await query_service.get_suggested_questions(
            transcript_ids=transcript_ids,
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