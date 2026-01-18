"""
ID Encryption Utility - Per-user ID obfuscation for secure API communication.

This module provides encryption/decryption of internal IDs using user-specific keys.
Prevents users from guessing or manipulating resource IDs in API requests.
"""

import base64
import hashlib
import secrets
import time
import logging
from typing import Optional, Dict, Tuple, Union
from cryptography.fernet import Fernet
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class IDEncryptionCache:
    """In-memory cache for user encryption keys with TTL."""
    
    def __init__(self, ttl_hours: int = 24):
        self._cache: Dict[str, Tuple[str, float]] = {}  # user_id -> (key, timestamp)
        self._ttl_seconds = ttl_hours * 3600
    
    def get(self, user_id: str) -> Optional[str]:
        """Get cached encryption key for user."""
        if user_id in self._cache:
            key, timestamp = self._cache[user_id]
            if time.time() - timestamp < self._ttl_seconds:
                return key
            else:
                # Expired, remove from cache
                del self._cache[user_id]
        return None
    
    def set(self, user_id: str, key: str) -> None:
        """Cache encryption key for user."""
        self._cache[user_id] = (key, time.time())
    
    def invalidate(self, user_id: str) -> None:
        """Remove user's key from cache (e.g., after key rotation)."""
        if user_id in self._cache:
            del self._cache[user_id]
            logger.info(f"Invalidated encryption key cache for user {user_id}")
    
    def clear(self) -> None:
        """Clear all cached keys."""
        self._cache.clear()


# Global cache instance
_key_cache = IDEncryptionCache(ttl_hours=24)


def generate_user_encryption_key() -> str:
    """
    Generate a new encryption key for a user.
    
    Returns:
        A URL-safe base64-encoded 32-byte key suitable for Fernet encryption.
    """
    return Fernet.generate_key().decode('utf-8')


def _get_fernet(user_key: str) -> Fernet:
    """Create Fernet instance from user's key."""
    return Fernet(user_key.encode('utf-8'))


def encrypt_id(internal_id: Union[int, str], user_key: str) -> str:
    """
    Encrypt an internal ID using user's encryption key.
    
    Args:
        internal_id: The actual database ID (int or string)
        user_key: User's encryption key
        
    Returns:
        Encrypted, URL-safe string representation of the ID
    """
    try:
        fernet = _get_fernet(user_key)
        # Add timestamp prefix to prevent replay attacks and add uniqueness
        data = f"{int(time.time() * 1000)}:{internal_id}".encode('utf-8')
        encrypted = fernet.encrypt(data)
        # Make it URL-safe by replacing characters
        return encrypted.decode('utf-8').replace('/', '_').replace('+', '-')
    except Exception as e:
        logger.error(f"ID encryption failed: {e}")
        raise ValueError("Failed to encrypt ID")


def decrypt_id(encrypted_id: str, user_key: str, max_age_hours: int = 72) -> Union[int, str]:
    """
    Decrypt an encrypted ID using user's encryption key.
    
    Args:
        encrypted_id: The encrypted ID from client
        user_key: User's encryption key
        max_age_hours: Maximum age of encrypted ID (prevents reuse of very old tokens)
        
    Returns:
        The original internal ID
        
    Raises:
        ValueError: If decryption fails or token is too old
    """
    try:
        fernet = _get_fernet(user_key)
        # Restore original base64 characters
        encrypted_bytes = encrypted_id.replace('_', '/').replace('-', '+').encode('utf-8')
        decrypted = fernet.decrypt(encrypted_bytes).decode('utf-8')
        
        # Parse timestamp and ID
        parts = decrypted.split(':', 1)
        if len(parts) != 2:
            raise ValueError("Invalid encrypted ID format")
        
        timestamp_ms, id_str = parts
        
        # Check age
        age_hours = (time.time() * 1000 - int(timestamp_ms)) / (1000 * 3600)
        if age_hours > max_age_hours:
            raise ValueError("Encrypted ID has expired")
        
        # Try to convert to int if it looks like a number
        try:
            return int(id_str)
        except ValueError:
            return id_str
            
    except Exception as e:
        logger.warning(f"ID decryption failed: {e}")
        raise ValueError("Invalid or tampered ID")


class UserIDEncryptor:
    """
    High-level class for managing ID encryption for a specific user.
    Handles caching and database lookups.
    """
    
    def __init__(self, db_session, user_id: str):
        self.db = db_session
        self.user_id = user_id
        self._key: Optional[str] = None
    
    def _get_key(self) -> str:
        """Get user's encryption key from cache or database."""
        if self._key:
            return self._key
        
        # Check cache first
        cached_key = _key_cache.get(self.user_id)
        if cached_key:
            self._key = cached_key
            return self._key
        
        # Fetch from database
        from models.user import User
        user = self.db.query(User).filter(User.id == self.user_id).first()
        if not user:
            raise ValueError(f"User {self.user_id} not found")
        
        if not user.encryption_key:
            # Generate key if not exists (migration case)
            user.encryption_key = generate_user_encryption_key()
            self.db.commit()
            logger.info(f"Generated encryption key for user {self.user_id}")
        
        self._key = user.encryption_key
        _key_cache.set(self.user_id, self._key)
        return self._key
    
    def encrypt(self, internal_id: Union[int, str]) -> str:
        """Encrypt an ID for sending to client."""
        return encrypt_id(internal_id, self._get_key())
    
    def decrypt(self, encrypted_id: str) -> Union[int, str]:
        """Decrypt an ID received from client."""
        return decrypt_id(encrypted_id, self._get_key())
    
    def encrypt_dict(self, data: dict, id_fields: list) -> dict:
        """
        Encrypt specified ID fields in a dictionary.
        
        Args:
            data: Dictionary containing response data
            id_fields: List of field names to encrypt (e.g., ['id', 'conversation_id'])
        """
        result = data.copy()
        for field in id_fields:
            if field in result and result[field] is not None:
                result[field] = self.encrypt(result[field])
        return result
    
    def decrypt_dict(self, data: dict, id_fields: list) -> dict:
        """
        Decrypt specified ID fields in a dictionary.
        
        Args:
            data: Dictionary containing request data
            id_fields: List of field names to decrypt
        """
        result = data.copy()
        for field in id_fields:
            if field in result and result[field] is not None:
                result[field] = self.decrypt(result[field])
        return result


def invalidate_user_key_cache(user_id: str) -> None:
    """Invalidate cached key for a user (call after key rotation)."""
    _key_cache.invalidate(user_id)


def rotate_user_key(db_session, user_id: str) -> str:
    """
    Rotate (regenerate) a user's encryption key.
    User will need to re-login to get new encrypted IDs.
    
    Args:
        db_session: Database session
        user_id: User ID to rotate key for
        
    Returns:
        The new encryption key
    """
    from models.user import User
    
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    new_key = generate_user_encryption_key()
    user.encryption_key = new_key
    user.encryption_key_rotated_at = datetime.utcnow()
    db_session.commit()
    
    # Invalidate cache
    invalidate_user_key_cache(user_id)
    
    logger.info(f"Rotated encryption key for user {user_id}")
    return new_key
