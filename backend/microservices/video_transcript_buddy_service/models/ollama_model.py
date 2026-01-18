"""
Ollama Model - Database model for tracking discovered Ollama models.

This table stores all Ollama models discovered via `npm run ollama:discover`.
Models are never deleted - only new ones are added and existing ones can be disabled.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, BigInteger, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import uuid


# Junction table: which models were available when a conversation was created
conversation_models = Table(
    'conversation_models',
    Base.metadata,
    Column('conversation_id', String, ForeignKey('conversations.id'), primary_key=True),
    Column('model_id', String, ForeignKey('ollama_models.id'), primary_key=True),
    Column('added_at', DateTime, server_default=func.now())
)


class OllamaModel(Base):
    """
    Tracks Ollama models discovered on the system.
    
    Models are discovered via `npm run ollama:discover` or `npm run ollama:latest-models`.
    Once discovered, models persist in the database and can be enabled/disabled.
    When a conversation is created, available models at that time are linked to it.
    """
    
    __tablename__ = "ollama_models"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Model identification
    name = Column(String(255), unique=True, nullable=False, index=True)  # e.g., "llama3.2:latest"
    model_family = Column(String(100), nullable=True)  # e.g., "llama"
    parameter_size = Column(String(50), nullable=True)  # e.g., "3.2B"
    quantization = Column(String(50), nullable=True)  # e.g., "Q4_K_M"
    
    # Model metadata
    description = Column(Text, nullable=True)  # Brief description
    size_bytes = Column(BigInteger, nullable=True)  # Size on disk
    digest = Column(String(255), nullable=True)  # Content hash for updates
    
    # Categories/capabilities (from Ollama library)
    capabilities = Column(String(255), nullable=True)  # e.g., "tools,vision,thinking"
    
    # Status
    is_installed = Column(Boolean, default=True)  # Currently installed locally
    is_enabled = Column(Boolean, default=True)  # User can disable models they don't want
    is_recommended = Column(Boolean, default=False)  # Mark good models for beginners
    
    # Discovery tracking
    discovered_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_checked_at = Column(DateTime, nullable=True)  # When we last checked if it's still installed
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        status = "✓" if self.is_installed and self.is_enabled else "✗"
        return f"<OllamaModel {self.name} ({self.parameter_size}) [{status}]>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "model_family": self.model_family,
            "parameter_size": self.parameter_size,
            "quantization": self.quantization,
            "description": self.description,
            "size_bytes": self.size_bytes,
            "size_human": self._human_readable_size(),
            "capabilities": self.capabilities.split(",") if self.capabilities else [],
            "is_installed": self.is_installed,
            "is_enabled": self.is_enabled,
            "is_recommended": self.is_recommended,
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None
        }
    
    def _human_readable_size(self):
        """Convert bytes to human readable format."""
        if not self.size_bytes:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(self.size_bytes) < 1024.0:
                return f"{self.size_bytes:.1f} {unit}"
            self.size_bytes /= 1024.0
        return f"{self.size_bytes:.1f} PB"


# Recommended models for beginners (popular, well-tested)
RECOMMENDED_MODELS = [
    "llama3.2",
    "llama3.1", 
    "mistral",
    "codellama",
    "phi3",
    "gemma2",
    "qwen2.5",
    "deepseek-coder"
]
