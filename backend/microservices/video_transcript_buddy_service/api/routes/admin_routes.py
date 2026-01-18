"""
Admin Routes - Administrative operations for system management.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from config.database import get_db
from api.dependencies.auth import get_current_user
from models.user import User
from utils.id_encryption import rotate_user_key, invalidate_user_key_cache

logger = logging.getLogger(__name__)

router = APIRouter()


class KeyRotationResponse(BaseModel):
    """Response for key rotation."""
    success: bool
    message: str
    user_id: str
    rotated_at: datetime


class UserKeyStatusResponse(BaseModel):
    """Response for user key status."""
    user_id: str
    email: str
    has_encryption_key: bool
    key_rotated_at: Optional[datetime]


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is admin (ENTERPRISE tier for now)."""
    if current_user.tier != "ENTERPRISE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post(
    "/users/{user_id}/rotate-encryption-key",
    response_model=KeyRotationResponse,
    summary="Rotate user's encryption key",
    description="Regenerate a user's ID encryption key. User will need to re-login."
)
async def rotate_user_encryption_key(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> KeyRotationResponse:
    """
    Rotate (regenerate) a user's encryption key.
    
    This invalidates all currently encrypted IDs for the user.
    The user will need to log out and log back in to receive new encrypted IDs.
    
    Use cases:
    - Security incident response
    - Regular key rotation policy
    - User-requested key regeneration
    """
    try:
        # Verify target user exists
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Rotate the key
        rotate_user_key(db, user_id)
        
        logger.info(f"Admin {current_user.email} rotated encryption key for user {user_id}")
        
        return KeyRotationResponse(
            success=True,
            message=f"Encryption key rotated for user {target_user.email}. User must re-login.",
            user_id=user_id,
            rotated_at=datetime.utcnow()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Key rotation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rotate encryption key"
        )


@router.get(
    "/users/{user_id}/encryption-key-status",
    response_model=UserKeyStatusResponse,
    summary="Get user's encryption key status",
    description="Check if user has an encryption key and when it was last rotated"
)
async def get_user_key_status(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> UserKeyStatusResponse:
    """Get encryption key status for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return UserKeyStatusResponse(
        user_id=user.id,
        email=user.email,
        has_encryption_key=user.encryption_key is not None,
        key_rotated_at=user.encryption_key_rotated_at
    )


@router.post(
    "/users/rotate-all-keys",
    summary="Rotate encryption keys for all users",
    description="Emergency operation: Rotate keys for all users. All users must re-login."
)
async def rotate_all_user_keys(
    confirm: bool = Query(False, description="Must be true to confirm this destructive operation"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Rotate encryption keys for ALL users.
    
    WARNING: This is a destructive operation that will:
    - Invalidate all encrypted IDs for all users
    - Require all users to log out and log back in
    
    Only use in emergency situations (e.g., suspected system-wide breach).
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to execute this operation"
        )
    
    users = db.query(User).all()
    rotated_count = 0
    
    for user in users:
        try:
            rotate_user_key(db, user.id)
            rotated_count += 1
        except Exception as e:
            logger.error(f"Failed to rotate key for user {user.id}: {e}")
    
    logger.warning(f"Admin {current_user.email} rotated ALL user encryption keys ({rotated_count} users)")
    
    return {
        "success": True,
        "message": f"Rotated encryption keys for {rotated_count} users",
        "total_users": len(users),
        "rotated_count": rotated_count
    }


@router.post(
    "/my/rotate-encryption-key",
    response_model=KeyRotationResponse,
    summary="Rotate own encryption key",
    description="User can rotate their own encryption key. Requires re-login."
)
async def rotate_own_encryption_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> KeyRotationResponse:
    """
    Allow users to rotate their own encryption key.
    After this, user should log out and log back in.
    """
    rotate_user_key(db, current_user.id)
    
    logger.info(f"User {current_user.email} rotated their own encryption key")
    
    return KeyRotationResponse(
        success=True,
        message="Your encryption key has been rotated. Please log out and log back in.",
        user_id=current_user.id,
        rotated_at=datetime.utcnow()
    )
