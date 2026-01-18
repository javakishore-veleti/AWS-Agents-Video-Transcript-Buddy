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
    max_uploads: int          # -1 for unlimited
    max_queries: int          # -1 for unlimited
    max_file_size_mb: int
    allowed_models: list      # List of allowed AI models
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


# Tier configurations based on pricing model
TIERS = {
    TierName.FREE: TierLimits(
        name=TierName.FREE,
        monthly_price=0.0,
        max_uploads=5,
        max_queries=10,
        max_file_size_mb=1,
        allowed_models=["basic"]
    ),
    TierName.STARTER: TierLimits(
        name=TierName.STARTER,
        monthly_price=29.0,
        max_uploads=50,
        max_queries=500,
        max_file_size_mb=10,
        allowed_models=["basic", "standard"]
    ),
    TierName.PRO: TierLimits(
        name=TierName.PRO,
        monthly_price=99.0,
        max_uploads=500,
        max_queries=5000,
        max_file_size_mb=50,
        allowed_models=["basic", "standard", "advanced"]
    ),
    TierName.ENTERPRISE: TierLimits(
        name=TierName.ENTERPRISE,
        monthly_price=-1.0,  # Custom pricing
        max_uploads=-1,       # Unlimited
        max_queries=-1,       # Unlimited
        max_file_size_mb=100,
        allowed_models=["basic", "standard", "advanced", "gpt-4", "claude"]
    ),
}


def get_tier_limits(tier_name: str) -> TierLimits:
    """Get limits for a tier by name."""
    try:
        tier = TierName(tier_name.upper())
        return TIERS[tier]
    except (ValueError, KeyError):
        return TIERS[TierName.FREE]