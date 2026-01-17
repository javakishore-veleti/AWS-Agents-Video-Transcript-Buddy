"""
Vector Store DAO - Data Access Object for vector embeddings storage.

Uses FAISS for local vector storage with OpenAI embeddings.
"""

import logging
import os
import json
import pickle
from typing import List, Optional, Dict, Any
from datetime import datetime

from config import settings
from utils.text_utils import chunk_text, clean_transcript_text
from common.exceptions import VectorStoreException
from common.constants import DEFAULT_SEARCH_RESULTS, MAX_SEARCH_RESULTS

logger = logging.getLogger(__name__)


class VectorStoreDAO:
    """Data Access Object for vector store operations using FAISS."""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "transcripts"
    ):
        """
        Initialize Vector Store DAO.
        
        Args:
            persist_directory: Directory for vector store persistence
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory or settings.VECTOR_STORE_PATH
        self.collection_name = collection_name
        self._index = None
        self._documents = []  # Store documents with metadata
        self._embeddings_model = None
        self._index_path = os.path.join(self.persist_directory, f"{collection_name}.faiss")
        self._docs_path = os.path.join(self.persist_directory, f"{collection_name}_docs.pkl")
    
    def _ensure_directory(self):
        """Ensure persist directory exists."""
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory, exist_ok=True)
            logger.info(f"Created vector store directory: {self.persist_directory}")
    
    def _get_embeddings_model(self):
        """Get OpenAI embeddings model."""
        if self._embeddings_model is None:
            try:
                from langchain_openai import OpenAIEmbeddings
                
                self._embeddings_model = OpenAIEmbeddings(
                    api_key=settings.OPENAI_API_KEY,
                    model=settings.OPENAI_EMBEDDING_MODEL
                )
            except Exception as e:
                logger.error(f"Failed to create embeddings model: {e}")
                raise VectorStoreException(
                    f"Failed to initialize embeddings: {str(e)}",
                    operation="init_embeddings"
                )
        
        return self._embeddings_model
    
    def _load_index(self):
        """Load existing index from disk."""
        if self._index is not None:
            return
        
        self._ensure_directory()
        
        try:
            import faiss
            
            if os.path.exists(self._index_path) and os.path.exists(self._docs_path):
                self._index = faiss.read_index(self._index_path)
                with open(self._docs_path, 'rb') as f:
                    self._documents = pickle.load(f)
                logger.info(f"Loaded existing index with {len(self._documents)} documents")
            else:
                # Create new index (1536 dimensions for OpenAI embeddings)
                self._index = faiss.IndexFlatL2(1536)
                self._documents = []
                logger.info("Created new FAISS index")
        
        except Exception as e:
            logger.error(f"Failed to load/create index: {e}")
            raise VectorStoreException(
                f"Failed to initialize vector store: {str(e)}",
                operation="init"
            )
    
    def _save_index(self):
        """Save index to disk."""
        try:
            import faiss
            
            self._ensure_directory()
            faiss.write_index(self._index, self._index_path)
            with open(self._docs_path, 'wb') as f:
                pickle.dump(self._documents, f)
            logger.info(f"Saved index with {len(self._documents)} documents")
        
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def index_transcript(
        self,
        transcript_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Index a transcript into the vector store.
        
        Args:
            transcript_id: Unique identifier for the transcript
            content: Transcript text content
            metadata: Additional metadata
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dict with indexing details
        """
        chunk_size = chunk_size or settings.VECTOR_CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.VECTOR_CHUNK_OVERLAP
        
        try:
            import numpy as np
            
            self._load_index()
            
            # Clean and chunk the content
            cleaned_content = clean_transcript_text(content)
            chunks = chunk_text(cleaned_content, chunk_size, chunk_overlap)
            
            if not chunks:
                logger.warning(f"No chunks generated for transcript: {transcript_id}")
                return {
                    "transcript_id": transcript_id,
                    "chunks_indexed": 0,
                    "status": "empty"
                }
            
            # Remove existing chunks for this transcript
            self._delete_transcript_chunks(transcript_id)
            
            # Get embeddings for all chunks
            embeddings_model = self._get_embeddings_model()
            embeddings = embeddings_model.embed_documents(chunks)
            
            # Add to index
            embeddings_array = np.array(embeddings).astype('float32')
            start_idx = len(self._documents)
            self._index.add(embeddings_array)
            
            # Store document metadata
            base_metadata = {
                "transcript_id": transcript_id,
                "indexed_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            for i, chunk in enumerate(chunks):
                self._documents.append({
                    "id": f"{transcript_id}_chunk_{i}",
                    "content": chunk,
                    "metadata": {
                        **base_metadata,
                        "chunk_index": i,
                        "chunk_count": len(chunks),
                        "chunk_length": len(chunk)
                    }
                })
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Indexed transcript {transcript_id}: {len(chunks)} chunks")
            
            return {
                "transcript_id": transcript_id,
                "chunks_indexed": len(chunks),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "status": "indexed"
            }
        
        except Exception as e:
            logger.error(f"Failed to index transcript {transcript_id}: {e}")
            raise VectorStoreException(
                f"Failed to index transcript: {str(e)}",
                operation="index"
            )
    
    def _delete_transcript_chunks(self, transcript_id: str):
        """Delete all chunks for a transcript (rebuilds index without them)."""
        try:
            import faiss
            import numpy as np
            
            self._load_index()
            
            # Find documents to keep
            docs_to_keep = [
                doc for doc in self._documents 
                if doc["metadata"].get("transcript_id") != transcript_id
            ]
            
            if len(docs_to_keep) == len(self._documents):
                return  # Nothing to delete
            
            deleted_count = len(self._documents) - len(docs_to_keep)
            
            if docs_to_keep:
                # Re-embed and rebuild index
                embeddings_model = self._get_embeddings_model()
                contents = [doc["content"] for doc in docs_to_keep]
                embeddings = embeddings_model.embed_documents(contents)
                embeddings_array = np.array(embeddings).astype('float32')
                
                # Create new index
                self._index = faiss.IndexFlatL2(1536)
                self._index.add(embeddings_array)
            else:
                # Empty index
                self._index = faiss.IndexFlatL2(1536)
            
            self._documents = docs_to_keep
            self._save_index()
            
            logger.info(f"Deleted {deleted_count} chunks for {transcript_id}")
        
        except Exception as e:
            logger.warning(f"Failed to delete existing chunks: {e}")
    
    def search(
        self,
        query: str,
        n_results: int = DEFAULT_SEARCH_RESULTS,
        transcript_ids: Optional[List[str]] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant transcript chunks.
        
        Args:
            query: Search query
            n_results: Number of results to return
            transcript_ids: Optional filter by transcript IDs
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of matching chunks with metadata
        """
        n_results = min(n_results, MAX_SEARCH_RESULTS)
        
        try:
            import numpy as np
            
            self._load_index()
            
            if len(self._documents) == 0:
                return []
            
            # Get query embedding
            embeddings_model = self._get_embeddings_model()
            query_embedding = embeddings_model.embed_query(query)
            query_array = np.array([query_embedding]).astype('float32')
            
            # Search
            k = min(n_results * 3, len(self._documents))  # Get extra for filtering
            distances, indices = self._index.search(query_array, k)
            
            # Process results
            search_results = []
            
            for i, idx in enumerate(indices[0]):
                if idx < 0 or idx >= len(self._documents):
                    continue
                
                doc = self._documents[idx]
                distance = distances[0][i]
                
                # Convert L2 distance to similarity score
                similarity = 1 / (1 + distance)
                
                # Filter by transcript_ids if specified
                if transcript_ids:
                    if doc["metadata"].get("transcript_id") not in transcript_ids:
                        continue
                
                # Filter by minimum score
                if similarity < min_score:
                    continue
                
                search_results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": round(similarity, 4),
                    "distance": round(float(distance), 4)
                })
                
                if len(search_results) >= n_results:
                    break
            
            logger.info(f"Search returned {len(search_results)} results for query: {query[:50]}...")
            return search_results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreException(
                f"Search failed: {str(e)}",
                operation="search"
            )
    
    def delete_transcript(self, transcript_id: str) -> bool:
        """
        Delete all chunks for a transcript.
        
        Args:
            transcript_id: Transcript identifier
            
        Returns:
            bool: True if deleted
        """
        try:
            self._delete_transcript_chunks(transcript_id)
            logger.info(f"Deleted transcript from vector store: {transcript_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete transcript {transcript_id}: {e}")
            return False
    
    def get_transcript_info(self, transcript_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about indexed transcript.
        
        Args:
            transcript_id: Transcript identifier
            
        Returns:
            Dict with transcript info or None
        """
        try:
            self._load_index()
            
            chunks = [
                doc for doc in self._documents 
                if doc["metadata"].get("transcript_id") == transcript_id
            ]
            
            if not chunks:
                return None
            
            first_metadata = chunks[0]["metadata"]
            
            return {
                "transcript_id": transcript_id,
                "chunk_count": len(chunks),
                "indexed_at": first_metadata.get("indexed_at"),
                "metadata": first_metadata
            }
        
        except Exception as e:
            logger.error(f"Failed to get transcript info: {e}")
            return None
    
    def list_indexed_transcripts(self) -> List[Dict[str, Any]]:
        """
        List all indexed transcripts.
        
        Returns:
            List of transcript info
        """
        try:
            self._load_index()
            
            # Group by transcript_id
            transcripts = {}
            for doc in self._documents:
                tid = doc["metadata"].get("transcript_id")
                if tid and tid not in transcripts:
                    transcripts[tid] = {
                        "transcript_id": tid,
                        "chunk_count": 0,
                        "indexed_at": doc["metadata"].get("indexed_at")
                    }
                if tid:
                    transcripts[tid]["chunk_count"] += 1
            
            return list(transcripts.values())
        
        except Exception as e:
            logger.error(f"Failed to list indexed transcripts: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dict with stats
        """
        try:
            self._load_index()
            
            transcripts = self.list_indexed_transcripts()
            
            return {
                "total_chunks": len(self._documents),
                "total_transcripts": len(transcripts),
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                "total_chunks": 0,
                "total_transcripts": 0,
                "error": str(e)
            }
    
    def clear(self) -> bool:
        """
        Clear all data from vector store.
        
        Returns:
            bool: True if cleared
        """
        try:
            import faiss
            
            self._index = faiss.IndexFlatL2(1536)
            self._documents = []
            
            # Remove files
            if os.path.exists(self._index_path):
                os.remove(self._index_path)
            if os.path.exists(self._docs_path):
                os.remove(self._docs_path)
            
            logger.info(f"Cleared vector store: {self.collection_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            return False
    
    # Compatibility property for tools that expect collection
    @property
    def collection(self):
        """Compatibility property - returns self for collection-like operations."""
        return self
    
    def get(self, where=None, include=None):
        """Compatibility method for ChromaDB-like get operations."""
        self._load_index()
        
        results = {"ids": [], "documents": [], "metadatas": []}
        
        for doc in self._documents:
            # Apply where filter if specified
            if where:
                match = True
                for key, value in where.items():
                    if key == "$and":
                        for condition in value:
                            for k, v in condition.items():
                                if doc["metadata"].get(k) != v:
                                    match = False
                                    break
                    elif doc["metadata"].get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            results["ids"].append(doc["id"])
            if include and "documents" in include:
                results["documents"].append(doc["content"])
            if include and "metadatas" in include:
                results["metadatas"].append(doc["metadata"])
        
        return results
    
    def count(self):
        """Return total number of documents."""
        self._load_index()
        return len(self._documents)