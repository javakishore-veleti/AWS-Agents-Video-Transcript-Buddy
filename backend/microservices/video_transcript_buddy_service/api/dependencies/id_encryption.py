"""
ID Encryption Dependency - FastAPI dependency for automatic ID encryption/decryption.
"""

from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from config.database import get_db
from api.dependencies.auth import get_current_user
from models.user import User
from utils.id_encryption import UserIDEncryptor, decrypt_id, _key_cache


def get_id_encryptor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserIDEncryptor:
    """
    Get an ID encryptor for the current user.
    Use this to encrypt IDs in responses.
    """
    return UserIDEncryptor(db, current_user.id)


def decrypt_conversation_id(
    conversation_id: str = Query(..., description="Encrypted conversation ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> int:
    """
    Decrypt a conversation ID from query parameter.
    Use as a dependency to automatically decrypt and validate.
    """
    encryptor = UserIDEncryptor(db, current_user.id)
    try:
        decrypted = encryptor.decrypt(conversation_id)
        if not isinstance(decrypted, int):
            raise ValueError("Invalid conversation ID format")
        return decrypted
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired conversation ID"
        )


def decrypt_optional_conversation_id(
    conversation_id: Optional[str] = Query(None, description="Encrypted conversation ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Optional[int]:
    """
    Decrypt an optional conversation ID from query parameter.
    Returns None if not provided.
    """
    if conversation_id is None:
        return None
    
    encryptor = UserIDEncryptor(db, current_user.id)
    try:
        decrypted = encryptor.decrypt(conversation_id)
        if not isinstance(decrypted, int):
            raise ValueError("Invalid conversation ID format")
        return decrypted
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired conversation ID"
        )


class EncryptedIDPath:
    """
    Dependency class for path parameters that are encrypted IDs.
    
    Usage:
        @router.get("/conversations/{conversation_id}")
        async def get_conversation(
            conversation_id: int = Depends(EncryptedIDPath("conversation_id"))
        ):
            # conversation_id is now the decrypted integer
    """
    
    def __init__(self, param_name: str):
        self.param_name = param_name
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        **kwargs
    ) -> int:
        encrypted_id = kwargs.get(self.param_name)
        if not encrypted_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing {self.param_name}"
            )
        
        encryptor = UserIDEncryptor(db, current_user.id)
        try:
            decrypted = encryptor.decrypt(encrypted_id)
            if not isinstance(decrypted, int):
                raise ValueError("Invalid ID format")
            return decrypted
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or expired {self.param_name}"
            )
