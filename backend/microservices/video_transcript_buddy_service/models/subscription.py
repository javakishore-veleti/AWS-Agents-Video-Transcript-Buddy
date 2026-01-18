"""
Subscription Model - Tier definitions with limits and pricing.
"""

from enum import Enum
from dataclasses import dataclass


class TierName(str, Enum):
    """Subscription tier names."""
    FREE = "FREE"
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


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