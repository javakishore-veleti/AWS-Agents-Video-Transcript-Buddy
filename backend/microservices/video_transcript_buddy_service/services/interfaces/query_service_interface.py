"""
Query Service Interface - Abstract base class for query operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IQueryService(ABC):
    """Interface for query service operations."""
    
    @abstractmethod
    async def query(
        self,
        question: str,
        transcript_ids: Optional[List[str]] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Process a user query against transcripts.
        
        Args:
            question: User's question
            transcript_ids: Optional filter by specific transcripts
            max_results: Maximum number of source chunks to consider
            
        Returns:
            Dict with answer and source references
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        transcript_ids: Optional[List[str]] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant transcript chunks without generating an answer.
        
        Args:
            query: Search query
            transcript_ids: Optional filter by specific transcripts
            max_results: Maximum number of results
            
        Returns:
            List of matching chunks with metadata
        """
        pass
    
    @abstractmethod
    async def validate_query(self, question: str) -> Dict[str, Any]:
        """
        Validate a user query before processing.
        
        Args:
            question: User's question
            
        Returns:
            Dict with validation result and any issues
        """
        pass
    
    @abstractmethod
    async def get_suggested_questions(
        self,
        transcript_ids: Optional[List[str]] = None,
        count: int = 5
    ) -> List[str]:
        """
        Get suggested questions based on transcript content.
        
        Args:
            transcript_ids: Optional filter by specific transcripts
            count: Number of suggestions
            
        Returns:
            List of suggested questions
        """
        pass