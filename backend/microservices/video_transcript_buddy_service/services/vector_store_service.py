"""
Vector Store Service - Business logic for vector store operations.
"""

import logging
from typing import List, Optional, Dict, Any

from .interfaces.vector_store_service_interface import IVectorStoreService
from dao.vector_store_dao import VectorStoreDAO

logger = logging.getLogger(__name__)


class VectorStoreService(IVectorStoreService):
    """Service for vector store operations."""
    
    def __init__(self, vector_store_dao: Optional[VectorStoreDAO] = None):
        """
        Initialize vector store service.
        
        Args:
            vector_store_dao: Vector store data access object
        """
        self.vector_store_dao = vector_store_dao or VectorStoreDAO()
    
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
        result = self.vector_store_dao.index_transcript(
            transcript_id=transcript_id,
            content=content,
            metadata=metadata
        )
        
        logger.info(f"Indexed transcript {transcript_id}: {result.get('chunks_indexed', 0)} chunks")
        
        return result
    
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
        results = self.vector_store_dao.search(
            query=query,
            n_results=n_results,
            transcript_ids=transcript_ids
        )
        
        logger.info(f"Search for '{query[:50]}...' returned {len(results)} results")
        
        return results
    
    async def delete_transcript(self, transcript_id: str) -> bool:
        """
        Delete transcript from vector store.
        
        Args:
            transcript_id: Transcript identifier
            
        Returns:
            bool: True if deleted
        """
        result = self.vector_store_dao.delete_transcript(transcript_id)
        
        if result:
            logger.info(f"Deleted transcript from vector store: {transcript_id}")
        else:
            logger.warning(f"Failed to delete transcript from vector store: {transcript_id}")
        
        return result
    
    async def get_transcript_info(self, transcript_id: str) -> Optional[Dict[str, Any]]:
        """
        Get info about indexed transcript.
        
        Args:
            transcript_id: Transcript identifier
            
        Returns:
            Dict with info or None
        """
        return self.vector_store_dao.get_transcript_info(transcript_id)
    
    async def list_indexed_transcripts(self) -> List[Dict[str, Any]]:
        """
        List all indexed transcripts.
        
        Returns:
            List of transcript info
        """
        return self.vector_store_dao.list_indexed_transcripts()
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dict with stats
        """
        return self.vector_store_dao.get_stats()
    
    async def clear(self) -> bool:
        """
        Clear all data from vector store.
        
        Returns:
            bool: True if cleared
        """
        result = self.vector_store_dao.clear()
        
        if result:
            logger.info("Cleared vector store")
        else:
            logger.warning("Failed to clear vector store")
        
        return result