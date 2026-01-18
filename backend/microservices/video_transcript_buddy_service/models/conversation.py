"""
Conversation Model - User workspace for organizing transcripts.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
import uuid

from config.database import Base


class Conversation(Base):
    """Conversation/Collection model for organizing transcripts."""
    
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    
    # LLM Settings - allows per-conversation model configuration
    llm_provider = Column(String(50), default="openai")  # openai, ollama, lmstudio, gemini, claude, etc.
    llm_model = Column(String(100), default="gpt-4")  # gpt-4, llama3.2, etc.
    llm_temperature = Column(Float, default=0.7)  # 0.0 to 1.0
    llm_base_url = Column(String(255), nullable=True)  # For custom endpoints
    
    # MCP Server (optional - for conversations using MCP)
    mcp_server_id = Column(String(36), ForeignKey("mcp_servers.id"), nullable=True)
    
    # Lock status (for tier downgrades)
    is_locked = Column(Boolean, default=False)
    lock_reason = Column(Text, nullable=True)  # JSON string with lock reasons
    locked_at = Column(DateTime, nullable=True)
    
    # Statistics
    file_count = Column(Integer, default=0)
    query_count = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    transcripts = relationship("Transcript", back_populates="conversation", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            # LLM Settings
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "llm_base_url": self.llm_base_url,
            # MCP
            "mcp_server_id": self.mcp_server_id,
            # Lock status
            "is_locked": self.is_locked,
            "lock_reason": self.lock_reason,
            "locked_at": self.locked_at.isoformat() if self.locked_at else None,
            # Statistics
            "file_count": self.file_count,
            "query_count": self.query_count,
            "total_size_mb": round(self.total_size_bytes / (1024 * 1024), 2),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
        }
    
    @staticmethod
    def generate_default_name() -> str:
        """Generate default conversation name from datetime."""
        return f"Conversation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def __repr__(self):
        return f"<Conversation {self.name} (User: {self.user_id})>"
