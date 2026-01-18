"""
Subscription Model - Tier definitions with limits and pricing.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from config.database import Base


class TierName(str, Enum):
    """Subscription tier names."""
    FREE = "FREE"
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    TRIAL = "TRIAL"


class Subscription(Base):
    """SQLAlchemy model for user subscriptions."""
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    tier = Column(SQLEnum(TierName), nullable=False, default=TierName.FREE)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="subscriptions")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tier": self.tier.value if self.tier else None,
            "status": self.status.value if self.status else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class TierLimits:
    """Limits for a subscription tier."""
    name: TierName
    monthly_price: float
    
    # Conversation limits
    max_conversations: int          # -1 for unlimited
    max_files_per_conversation: int # -1 for unlimited
    max_queries_per_conversation: int  # -1 for unlimited
    max_query_time_seconds: int     # Max time for a single query
    
    # File limits
    max_uploads: int                # Total uploads per month (-1 for unlimited)
    max_queries: int                # Total queries per month (-1 for unlimited)
    max_file_size_mb: int
    allowed_file_types: list        # ['txt', 'srt', 'vtt', 'json']
    
    # AI/Model limits
    allowed_models: list            # List of allowed AI models
    max_output_tokens: int          # Max tokens in response
    enable_intelligent_summary: bool # Advanced analysis features
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


# Tier configurations based on pricing model
TIERS = {
    TierName.FREE: TierLimits(
        name=TierName.FREE,
        monthly_price=0.0,
        max_conversations=3,
        max_files_per_conversation=5,
        max_queries_per_conversation=10,
        max_query_time_seconds=30,
        max_uploads=5,
        max_queries=10,
        max_file_size_mb=1,
        allowed_file_types=['txt', 'srt'],
        allowed_models=["basic"],
        max_output_tokens=500,
        enable_intelligent_summary=False
    ),
    TierName.STARTER: TierLimits(
        name=TierName.STARTER,
        monthly_price=29.0,
        max_conversations=10,
        max_files_per_conversation=20,
        max_queries_per_conversation=100,
        max_query_time_seconds=60,
        max_uploads=50,
        max_queries=500,
        max_file_size_mb=10,
        allowed_file_types=['txt', 'srt', 'vtt', 'json'],
        allowed_models=["basic", "standard"],
        max_output_tokens=2000,
        enable_intelligent_summary=True
    ),
    TierName.PRO: TierLimits(
        name=TierName.PRO,
        monthly_price=99.0,
        max_conversations=50,
        max_files_per_conversation=100,
        max_queries_per_conversation=1000,
        max_query_time_seconds=120,
        max_uploads=500,
        max_queries=5000,
        max_file_size_mb=50,
        allowed_file_types=['txt', 'srt', 'vtt', 'json', 'pdf'],
        allowed_models=["basic", "standard", "advanced"],
        max_output_tokens=4000,
        enable_intelligent_summary=True
    ),
    TierName.ENTERPRISE: TierLimits(
        name=TierName.ENTERPRISE,
        monthly_price=-1.0,  # Custom pricing
        max_conversations=-1,       # Unlimited
        max_files_per_conversation=-1,  # Unlimited
        max_queries_per_conversation=-1,  # Unlimited
        max_query_time_seconds=300,
        max_uploads=-1,       # Unlimited
        max_queries=-1,       # Unlimited
        max_file_size_mb=100,
        allowed_file_types=['txt', 'srt', 'vtt', 'json', 'pdf', 'docx'],
        allowed_models=["basic", "standard", "advanced", "gpt-4", "claude"],
        max_output_tokens=8000,
        enable_intelligent_summary=True
    ),
}


def get_tier_limits(tier_name: str) -> TierLimits:
    """Get limits for a tier by name."""
    try:
        tier = TierName(tier_name.upper())
        return TIERS[tier]
    except (ValueError, KeyError):
        return TIERS[TierName.FREE]