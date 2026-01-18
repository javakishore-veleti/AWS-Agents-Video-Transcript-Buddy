"""
Transcript Service v2 - Business logic with database and local/S3 storage support.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from dao.s3_dao import S3DAO
from dao.local_storage_dao import LocalStorageDAO
from dao.vector_store_dao import VectorStoreDAO
from models.transcript import Transcript
from models.conversation import Conversation
from config import settings
from common.exceptions import TranscriptNotFoundException, ValidationException
from utils.text_utils import is_supported_file, validate_file_size

logger = logging.getLogger(__name__)


class TranscriptServiceV2:
    """Service for transcript operations with database and flexible storage."""
    
    def __init__(self):
        """Initialize transcript service."""
        self.use_s3 = settings.USE_S3_STORAGE
        self.s3_dao = S3DAO() if self.use_s3 else None
        self.local_storage_dao = LocalStorageDAO()
        self.vector_store_dao = VectorStoreDAO()
        
        logger.info(f"TranscriptService initialized with storage: {'S3' if self.use_s3 else 'Local'}")
    
    async def upload_transcript(
        self,
        filename: str,
        content: bytes,
        user_id: str,
        conversation_id: int,
        db: Session,
        auto_index: bool = True
    ) -> Dict[str, Any]:
        """Upload and store transcript with database tracking."""
        # Validate
        if not is_supported_file(filename):
            raise ValidationException(f"Unsupported file type: {filename}")
        validate_file_size(len(content))
        
        # Store file
        if self.use_s3:
            upload_result = self.s3_dao.upload_transcript(filename, content)
            storage_type, storage_path = "s3", upload_result.get("s3_key")
        else:
            upload_result = self.local_storage_dao.upload_transcript(filename, content, user_id)
            storage_type, storage_path = "local", upload_result.get("filepath")
        
        # Create DB record
        transcript = Transcript(
            filename=filename,
            original_filename=filename,
            user_id=user_id,
            conversation_id=conversation_id,
            file_size=len(content),
            file_type=filename.split('.')[-1].lower(),
            storage_type=storage_type,
            local_path=storage_path if storage_type == "local" else None,
            s3_key=storage_path if storage_type == "s3" else None
        )
        
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        
        # Auto-index
        if auto_index:
            try:
                text_content = content.decode('utf-8')
                index_result = self.vector_store_dao.index_transcript(
                    transcript_id=transcript.id,
                    content=text_content,
                    metadata={
                        "filename": filename,
                        "user_id": user_id,  # CRITICAL: Multi-tenancy isolation
                        "conversation_id": str(conversation_id)  # For conversation-scoped queries
                    }
                )
                
                transcript.is_indexed = index_result.get("status") == "indexed"
                transcript.indexed_at = datetime.utcnow() if transcript.is_indexed else None
                transcript.chunk_count = index_result.get("chunks_indexed", 0)
                db.commit()
            except Exception as e:
                logger.error(f"Auto-indexing failed for {filename}: {e}")
        
        logger.info(f"Uploaded: {filename} (user: {user_id}, storage: {storage_type})")
        
        # Update conversation file count and size
        self._update_conversation_stats(db, conversation_id, file_count_delta=1, size_delta_bytes=len(content))
        
        return {
            "id": transcript.id,
            "filename": transcript.filename,
            "size": transcript.file_size,
            "storage_type": transcript.storage_type,
            "indexed": transcript.is_indexed,
            "uploaded_at": transcript.created_at.isoformat()
        }
    
    def _update_conversation_stats(
        self,
        db: Session,
        conversation_id: int,
        file_count_delta: int = 0,
        query_count_delta: int = 0,
        size_delta_bytes: int = 0
    ):
        """Update conversation statistics after file operations."""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        
        if conversation:
            conversation.file_count += file_count_delta
            conversation.query_count += query_count_delta
            conversation.total_size_bytes += size_delta_bytes
            conversation.last_activity_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Updated conversation {conversation_id} stats: files={conversation.file_count}, size={conversation.total_size_bytes}")
    
    async def list_transcripts(
        self, 
        db: Session, 
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all transcripts from database, optionally filtered by conversation."""
        query = db.query(Transcript)
        if user_id:
            query = query.filter(Transcript.user_id == user_id)
        if conversation_id:
            query = query.filter(Transcript.conversation_id == conversation_id)
        
        transcripts = query.order_by(Transcript.created_at.desc()).all()
        return [t.to_dict() for t in transcripts]
    
    async def get_transcript(self, transcript_id: str, db: Session) -> Dict[str, Any]:
        """Get transcript metadata from database."""
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            raise TranscriptNotFoundException(f"Transcript not found: {transcript_id}")
        return transcript.to_dict()
    
    async def get_transcript_content(self, transcript_id: str, db: Session) -> bytes:
        """Get transcript file content."""
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            raise TranscriptNotFoundException(f"Transcript not found: {transcript_id}")
        
        if transcript.storage_type == "s3":
            return self.s3_dao.get_transcript(transcript.filename)
        else:
            return self.local_storage_dao.get_transcript(transcript.filename)
    
    async def delete_transcript(self, transcript_id: str, db: Session) -> bool:
        """Delete transcript from storage and database."""
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            raise TranscriptNotFoundException(f"Transcript not found: {transcript_id}")
        
        # Store conversation_id and file_size before deletion
        conversation_id = transcript.conversation_id
        file_size = transcript.file_size
        
        # Delete from storage
        if transcript.storage_type == "s3":
            self.s3_dao.delete_transcript(transcript.filename)
        else:
            self.local_storage_dao.delete_transcript(transcript.filename)
        
        # Delete from vector store
        self.vector_store_dao.delete_transcript(transcript_id)
        
        # Delete from database
        db.delete(transcript)
        db.commit()
        
        # Update conversation stats (decrement)
        if conversation_id:
            self._update_conversation_stats(db, conversation_id, file_count_delta=-1, size_delta_bytes=-file_size)
        
        logger.info(f"Deleted transcript: {transcript_id}")
        return True
