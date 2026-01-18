"""
Auth Service Interface - Abstract base class for authentication operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from models.user import User


class IAuthService(ABC):
    """Interface for authentication service operations."""
    
    @abstractmethod
    def register(self, email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        Register a new user.
        
        Args:
            email: User email
            password: Plain text password
            full_name: Optional full name
            
        Returns:
            Created User
        """
        pass
    
    @abstractmethod
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and return tokens.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Dict with access_token, refresh_token, user info
        """
        pass
    
    @abstractmethod
    def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict with new access_token
        """
        pass
    
    @abstractmethod
    def get_current_user(self, token: str) -> User:
        """
        Get user from access token.
        
        Args:
            token: JWT access token
            
        Returns:
            User object
        """
        pass
