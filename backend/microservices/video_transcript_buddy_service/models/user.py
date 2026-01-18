"""
User Model - User accounts with subscription tier.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from config.database import Base


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Subscription
    tier = Column(String(20), default="FREE", nullable=False)  # FREE, STARTER, PRO, ENTERPRISE
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email} ({self.tier})>"