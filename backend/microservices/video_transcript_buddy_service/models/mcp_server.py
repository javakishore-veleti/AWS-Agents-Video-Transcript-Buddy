"""
MCP Server Model - Database model for user MCP server configurations.

MCP (Model Context Protocol) servers allow users to connect external tools and data sources.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from config.database import Base


class MCPServerStatus(str, Enum):
    """MCP Server connection status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class MCPServer(Base):
    """User-configured MCP server."""
    
    __tablename__ = "mcp_servers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Server configuration
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    server_url = Column(String(500), nullable=False)
    server_type = Column(String(50), default="stdio")  # stdio, http, websocket
    
    # Authentication
    auth_type = Column(String(50), default="none")  # none, api_key, oauth, bearer
    auth_token_encrypted = Column(Text, nullable=True)  # Encrypted credentials
    
    # Status
    status = Column(SQLEnum(MCPServerStatus), default=MCPServerStatus.PENDING)
    last_health_check = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Capabilities (discovered from server)
    capabilities_json = Column(Text, nullable=True)  # JSON of available tools/resources
    
    # Metadata
    is_default = Column(Boolean, default=False)  # Default server for new conversations
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mcp_servers")
    
    def to_dict(self):
        """Convert to dictionary (without sensitive data)."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "server_url": self.server_url,
            "server_type": self.server_type,
            "auth_type": self.auth_type,
            "status": self.status.value if self.status else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ConversationMCPServer(Base):
    """Association between conversation and MCP server."""
    
    __tablename__ = "conversation_mcp_servers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    mcp_server_id = Column(String(36), ForeignKey("mcp_servers.id"), nullable=False, index=True)
    
    # Override settings for this conversation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
