"""
Usage Model - Track uploads, queries, and costs per user.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid

from config.database import Base


class UsageType(str, Enum):
    """Types of usage to track."""
    UPLOAD = "UPLOAD"
    QUERY_SIMPLE = "QUERY_SIMPLE"
    QUERY_COMPLEX = "QUERY_COMPLEX"
    TRANSCRIPTION = "TRANSCRIPTION"


class UsageRecord(Base):
    """Track individual usage events."""
    
    __tablename__ = "usage_records"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Usage details
    usage_type = Column(String(20), nullable=False)  # UPLOAD, QUERY_SIMPLE, QUERY_COMPLEX, TRANSCRIPTION
    quantity = Column(Float, default=1.0)            # Count or minutes for transcription
    file_size_bytes = Column(Integer, nullable=True) # For uploads
    model_used = Column(String(50), nullable=True)   # gpt-4, claude, etc.
    
    # Cost breakdown
    base_cost = Column(Float, default=0.0)
    model_surcharge = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="usage_records")
    
    def __repr__(self):
        return f"<UsageRecord {self.usage_type} ${self.total_cost:.2f}>"