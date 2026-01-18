"""
Auth Service - User registration, login, and token management.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .interfaces.auth_service_interface import IAuthService
from models.user import User
from utils.auth_utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from common.exceptions import ValidationException, AuthenticationException

logger = logging.getLogger(__name__)


class AuthService(IAuthService):
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        Register a new user.
        
        Args:
            email: User email
            password: Plain text password
            full_name: Optional full name
            
        Returns:
            Created User
            
        Raises:
            ValidationException: If email already exists
        """
        # Check if email exists
        existing = self.db.query(User).filter(User.email == email.lower()).first()
        if existing:
            raise ValidationException("Email already registered", field="email")
        
        # Create user
        user = User(
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name=full_name,
            tier="FREE"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User registered: {user.email}")
        return user
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and return tokens.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Dict with access_token, refresh_token, user info
            
        Raises:
            AuthenticationException: If credentials invalid
        """
        user = self.db.query(User).filter(User.email == email.lower()).first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationException("Account is deactivated")
        
        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "tier": user.tier
            }
        }
    
    def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict with new access_token
            
        Raises:
            AuthenticationException: If token invalid
        """
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationException("Invalid refresh token")
        
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")
        
        new_access_token = create_access_token(user.id)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    
    def get_current_user(self, token: str) -> User:
        """
        Get user from access token.
        
        Args:
            token: JWT access token
            
        Returns:
            User object
            
        Raises:
            AuthenticationException: If token invalid
        """
        payload = decode_token(token)
        
        if not payload or payload.get("type") != "access":
            raise AuthenticationException("Invalid access token")
        
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")
        
        return user
