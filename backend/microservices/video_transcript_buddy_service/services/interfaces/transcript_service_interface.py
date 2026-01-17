"""
Transcript Service Interface - Abstract base class for transcript operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class ITranscriptService(ABC):
    """Interface for transcript service operations."""
    
    @abstractmethod
    async def upload_transcript(
        self,
        filename: str,
        content: bytes,
        auto_index: bool = True
    ) -> Dict[str, Any]:
        """
        Upload a transcript file.
        
        Args:
            filename: Name of the file
            content: File content as bytes
            auto_index: Whether to automatically index in vector store
            
        Returns:
            Dict with upload details
        """
        pass
    
    @abstractmethod
    async def get_transcript(self, filename: str) -> Dict[str, Any]:
        """
        Get transcript content and metadata.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dict with content and metadata
        """
        pass
    
    @abstractmethod
    async def delete_transcript(self, filename: str) -> bool:
        """
        Delete a transcript.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if deleted
        """
        pass
    
    @abstractmethod
    async def list_transcripts(self) -> List[Dict[str, Any]]:
        """
        List all transcripts.
        
        Returns:
            List of transcript details
        """
        pass
    
    @abstractmethod
    async def transcript_exists(self, filename: str) -> bool:
        """
        Check if transcript exists.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if exists
        """
        pass
    
    @abstractmethod
    async def reindex_transcript(self, filename: str) -> Dict[str, Any]:
        """
        Reindex a transcript in vector store.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dict with indexing details
        """
        pass
    
    @abstractmethod
    async def reindex_all_transcripts(self) -> Dict[str, Any]:
        """
        Reindex all transcripts in vector store.
        
        Returns:
            Dict with indexing summary
        """
        pass