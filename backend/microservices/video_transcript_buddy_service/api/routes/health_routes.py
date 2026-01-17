"""
Health Routes - Health check endpoints for the service.
"""

from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime

from config import settings
from utils.aws_utils import validate_aws_credentials, check_s3_bucket_exists
from dao.vector_store_dao import VectorStoreDAO

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic health status of the service"
)
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Checks if the service is ready to handle requests"
)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - verifies all dependencies are available.
    """
    checks = {
        "aws_credentials": False,
        "s3_bucket": False,
        "vector_store": False,
        "openai_api": False
    }
    
    # Check AWS credentials
    is_valid, error = validate_aws_credentials()
    checks["aws_credentials"] = is_valid
    
    # Check S3 bucket
    if settings.S3_BUCKET_NAME:
        exists, error = check_s3_bucket_exists(settings.S3_BUCKET_NAME)
        checks["s3_bucket"] = exists
    
    # Check vector store
    try:
        vector_store = VectorStoreDAO()
        stats = vector_store.get_stats()
        checks["vector_store"] = "error" not in stats
    except Exception:
        checks["vector_store"] = False
    
    # Check OpenAI API key
    checks["openai_api"] = bool(settings.OPENAI_API_KEY)
    
    # Determine overall status
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Simple check to verify the service is running"
)
async def liveness_check() -> Dict[str, str]:
    """Liveness check - just verifies the service is running."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/details",
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Returns detailed health information including configuration"
)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with configuration info.
    """
    # Get vector store stats
    vector_stats = {}
    try:
        vector_store = VectorStoreDAO()
        vector_stats = vector_store.get_stats()
    except Exception as e:
        vector_stats = {"error": str(e)}
    
    # AWS status
    aws_valid, aws_error = validate_aws_credentials()
    
    return {
        "status": "healthy",
        "service": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL
        },
        "configuration": {
            "aws_region": settings.AWS_REGION,
            "s3_bucket": settings.S3_BUCKET_NAME or "(not configured)",
            "s3_transcript_folder": settings.S3_TRANSCRIPT_FOLDER,
            "vector_store_type": settings.VECTOR_STORE_TYPE,
            "openai_model": settings.OPENAI_MODEL,
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL
        },
        "dependencies": {
            "aws": {
                "status": "connected" if aws_valid else "error",
                "error": aws_error
            },
            "vector_store": vector_stats
        },
        "timestamp": datetime.utcnow().isoformat()
    }