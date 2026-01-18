"""
Usage Service Interface - Abstract base class for usage tracking operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime


class IUsageService(ABC):
    """Interface for usage tracking service operations."""
    
    @abstractmethod
    def record_upload(
        self,
        user_id: str,
        file_size_bytes: int,
        filename: str
    ) -> Dict[str, Any]:
        """
        Record a file upload.
        
        Args:
            user_id: User ID
            file_size_bytes: Size of uploaded file
            filename: Name of the file
            
        Returns:
            Dict with usage record details
        """
        pass
    
    @abstractmethod
    def record_query(
        self,
        user_id: str,
        is_complex: bool,
        model_used: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a query.
        
        Args:
            user_id: User ID
            is_complex: Whether it's a complex query
            model_used: AI model used (for surcharge)
            
        Returns:
            Dict with usage record details
        """
        pass
    
    @abstractmethod
    def get_user_usage_summary(
        self,
        user_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get usage summary for a user.
        
        Args:
            user_id: User ID
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            Dict with usage counts and costs
        """
        pass
    
    @abstractmethod
    def check_limit(
        self,
        user_id: str,
        usage_type: str
    ) -> Dict[str, Any]:
        """
        Check if user is within tier limits.
        
        Args:
            user_id: User ID
            usage_type: UPLOAD or QUERY
            
        Returns:
            Dict with allowed status and remaining quota
        """
        pass