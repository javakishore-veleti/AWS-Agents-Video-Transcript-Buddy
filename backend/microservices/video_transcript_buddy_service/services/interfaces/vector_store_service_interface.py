"""
Vector Store Service Interface - Abstract base class for vector store operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IVectorStoreService(ABC):
    """Interface for vector store service operations."""
    
    @abstractmethod
    async def index_transcript(
        self,
        transcript_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Index a transcript into the vector store.
        
        Args:
            transcript_id: Unique identifier for the transcript
            content: Transcript text content
            metadata: Additional metadata
            
        Returns:
            Dict with indexing details
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        n_results: int = 5,
        transcript_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query
            n_results: Number of results
            transcript_ids: Optional filter by transcript IDs
            
        Returns:
            List of matching chunks
        """
        pass
    
    @abstractmethod
    async def delete_transcript(self, transcript_id: str) -> bool:
        """
        Delete transcript from vector store.
        
        Args:
            transcript_id: Transcript identifier
            
        Returns:
            bool: True if deleted
        """
        pass
    
    @abstractmethod
    async def get_transcript_info(self, transcript_id: str) -> Optional[Dict[str, Any]]:
        """
        Get info about indexed transcript.
        
        Args:
            transcript_id: Transcript identifier
            
        Returns:
            Dict with info or None
        """
        pass
    
    @abstractmethod
    async def list_indexed_transcripts(self) -> List[Dict[str, Any]]:
        """
        List all indexed transcripts.
        
        Returns:
            List of transcript info
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dict with stats
        """
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear all data from vector store.
        
        Returns:
            bool: True if cleared
        """
        pass