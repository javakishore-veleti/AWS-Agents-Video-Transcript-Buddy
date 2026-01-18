"""
Transcript Service - Business logic for transcript operations.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from .interfaces.transcript_service_interface import ITranscriptService
from dao.s3_dao import S3DAO
from dao.local_storage_dao import LocalStorageDAO
from dao.vector_store_dao import VectorStoreDAO
from models.transcript import Transcript
from config import settings
from common.exceptions import TranscriptNotFoundException, ValidationException
from utils.text_utils import is_supported_file, validate_file_size

logger = logging.getLogger(__name__)


class TranscriptService(ITranscriptService):
    """Service for transcript operations."""
    
    def __init__(
        self,
        s3_dao: Optional[S3DAO] = None,
        local_storage_dao: Optional[LocalStorageDAO] = None,
        vector_store_dao: Optional[VectorStoreDAO] = None
    ):
        """
        Initialize transcript service.
        
        Args:
            s3_dao: S3 data access object (optional, only if USE_S3_STORAGE is True)
            local_storage_dao: Local storage data access object
            vector_store_dao: Vector store data access object
        """
        self.use_s3 = settings.USE_S3_STORAGE
        self.s3_dao = s3_dao if self.use_s3 else None
        self.local_storage_dao = local_storage_dao or LocalStorageDAO()
        self.vector_store_dao = vector_store_dao or VectorStoreDAO()
        
        if self.use_s3 and self.s3_dao is None:
            self.s3_dao = S3DAO()
        
        logger.info(f"TranscriptService initialized with storage: {'S3' if self.use_s3 else 'Local'}")
    
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
        # Validate file type
        if not is_supported_file(filename):
            raise ValidationException(
                "Unsupported file type. Supported: .txt, .srt, .vtt, .json",
                field="filename"
            )
        
        # Validate file size
        if not validate_file_size(len(content)):
            raise ValidationException(
                "File size exceeds maximum allowed (50MB)",
                field="content"
            )
        
        # Ensure bucket exists
        self.s3_dao.ensure_bucket_exists()
        
        # Upload to S3
        upload_result = self.s3_dao.upload_transcript(
            filename=filename,
            content=content,
            content_type="text/plain"
        )
        
        # Auto-index if requested
        index_result = None
        if auto_index:
            try:
                text_content = content.decode('utf-8')
                index_result = self.vector_store_dao.index_transcript(
                    transcript_id=filename,
                    content=text_content,
                    metadata={"filename": filename}
                )
                
                # Update S3 metadata to mark as indexed
                self.s3_dao.update_metadata(filename, {"indexed": "true"})
                
            except Exception as e:
                logger.error(f"Auto-indexing failed for {filename}: {e}")
                index_result = {"status": "failed", "error": str(e)}
        
        return {
            **upload_result,
            "indexed": index_result is not None and index_result.get("status") == "indexed",
            "index_result": index_result
        }
    
    async def get_transcript(self, filename: str) -> Dict[str, Any]:
        """
        Get transcript content and metadata.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dict with content and metadata
        """
        transcript = self.s3_dao.download_transcript(filename)
        
        # Get vector store info
        vector_info = self.vector_store_dao.get_transcript_info(filename)
        
        return {
            **transcript,
            "vector_store_info": vector_info
        }
    
    async def delete_transcript(self, filename: str) -> bool:
        """
        Delete a transcript from S3 and vector store.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if deleted
        """
        # Delete from S3
        s3_deleted = self.s3_dao.delete_transcript(filename)
        
        # Delete from vector store
        vector_deleted = self.vector_store_dao.delete_transcript(filename)
        
        logger.info(f"Deleted transcript {filename}: S3={s3_deleted}, Vector={vector_deleted}")
        
        return s3_deleted
    
    async def list_transcripts(self) -> List[Dict[str, Any]]:
        """
        List all transcripts with their indexing status.
        
        Returns:
            List of transcript details
        """
        # Get transcripts from S3
        transcripts = self.s3_dao.list_transcripts()
        
        # Get indexed transcripts from vector store
        indexed_transcripts = self.vector_store_dao.list_indexed_transcripts()
        indexed_ids = {t["transcript_id"] for t in indexed_transcripts}
        
        # Merge information
        for transcript in transcripts:
            transcript["indexed"] = transcript["filename"] in indexed_ids
            
            # Get chunk count if indexed
            if transcript["indexed"]:
                info = self.vector_store_dao.get_transcript_info(transcript["filename"])
                transcript["chunk_count"] = info.get("chunk_count", 0) if info else 0
        
        return transcripts
    
    async def transcript_exists(self, filename: str) -> bool:
        """
        Check if transcript exists.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if exists
        """
        return self.s3_dao.transcript_exists(filename)
    
    async def reindex_transcript(self, filename: str) -> Dict[str, Any]:
        """
        Reindex a transcript in vector store.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dict with indexing details
        """
        # Get transcript content
        transcript = self.s3_dao.download_transcript(filename)
        
        # Reindex
        index_result = self.vector_store_dao.index_transcript(
            transcript_id=filename,
            content=transcript["content"],
            metadata={"filename": filename}
        )
        
        # Update S3 metadata
        if index_result.get("status") == "indexed":
            self.s3_dao.update_metadata(filename, {"indexed": "true"})
        
        return {
            "filename": filename,
            **index_result
        }
    
    async def reindex_all_transcripts(self) -> Dict[str, Any]:
        """
        Reindex all transcripts in vector store.
        
        Returns:
            Dict with indexing summary
        """
        transcripts = self.s3_dao.list_transcripts()
        
        results = {
            "total": len(transcripts),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for transcript in transcripts:
            try:
                result = await self.reindex_transcript(transcript["filename"])
                results["success"] += 1
                results["details"].append({
                    "filename": transcript["filename"],
                    "status": "success",
                    "chunks": result.get("chunks_indexed", 0)
                })
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "filename": transcript["filename"],
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"Failed to reindex {transcript['filename']}: {e}")
        
        return results