"""
Transcript Model - Database model for transcript metadata.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from config.database import Base
import uuid


class Transcript(Base):
    """Transcript metadata stored in database."""
    
    __tablename__ = "transcripts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False, unique=True, index=True)
    original_filename = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # File metadata
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String, nullable=False)  # txt, srt, vtt, json
    
    # Storage locations
    local_path = Column(String, nullable=True)  # Local file path if stored locally
    s3_key = Column(String, nullable=True)  # S3 key if stored in S3
    storage_type = Column(String, default="local")  # 'local' or 's3'
    
    # Indexing status
    is_indexed = Column(Boolean, default=False)
    indexed_at = Column(DateTime, nullable=True)
    chunk_count = Column(Integer, default=0)
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "user_id": self.user_id,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "storage_type": self.storage_type,
            "is_indexed": self.is_indexed,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "chunk_count": self.chunk_count,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
