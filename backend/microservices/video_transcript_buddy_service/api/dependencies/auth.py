"""
Auth Dependencies - FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from config.database import get_db
from services.auth_service import AuthService
from services.usage_service import UsageService
from models.user import User
from models.subscription import get_tier_limits
from common.exceptions import AuthenticationException


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        auth_service = AuthService(db)
        return auth_service.get_current_user(token)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.to_dict()
        )


async def check_upload_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Check if user can upload (within tier limit).
    """
    usage_service = UsageService(db)
    result = usage_service.check_limit(current_user.id, "UPLOAD")
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": True,
                "error_code": "UPLOAD_LIMIT_REACHED",
                "message": result["reason"],
                "limit": result["limit"],
                "current": result["current"]
            }
        )
    
    return current_user


async def check_query_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Check if user can query (within tier limit).
    """
    usage_service = UsageService(db)
    result = usage_service.check_limit(current_user.id, "QUERY")
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": True,
                "error_code": "QUERY_LIMIT_REACHED",
                "message": result["reason"],
                "limit": result["limit"],
                "current": result["current"]
            }
        )
    
    return current_user


async def check_file_size_limit(
    file_size: int,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Check if file size is within tier limit.
    """
    tier_limits = get_tier_limits(current_user.tier)
    max_bytes = tier_limits.max_file_size_bytes
    
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": True,
                "error_code": "FILE_TOO_LARGE",
                "message": f"File exceeds {tier_limits.max_file_size_mb}MB limit for {current_user.tier} tier",
                "max_size_mb": tier_limits.max_file_size_mb
            }
        )