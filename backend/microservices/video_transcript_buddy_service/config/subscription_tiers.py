"""
Subscription Tier Configuration - Defines limits and features per tier.

This configuration controls what features are available based on user subscription level.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


class SubscriptionTier(str, Enum):
    """User subscription tiers."""
    FREE = "FREE"
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


@dataclass
class TierLimits:
    """Limits for a subscription tier."""
    # Conversation limits
    max_conversations: int
    max_files_per_conversation: int
    max_total_storage_mb: int
    
    # Query limits
    queries_per_day: int
    queries_per_month: int
    
    # LLM Provider access
    allowed_providers: List[str]
    
    # MCP Server limits
    max_mcp_servers: int
    
    # Features
    can_use_local_models: bool
    can_use_cloud_models: bool
    can_use_mcp: bool
    can_use_agentic: bool  # n8n, etc.
    
    # Priority
    priority_support: bool
    priority_queue: bool


# Tier configurations
TIER_CONFIGS: Dict[SubscriptionTier, TierLimits] = {
    SubscriptionTier.FREE: TierLimits(
        max_conversations=3,
        max_files_per_conversation=5,
        max_total_storage_mb=50,
        queries_per_day=20,
        queries_per_month=200,
        allowed_providers=["openai", "ollama", "lmstudio"],  # Basic providers only
        max_mcp_servers=1,
        can_use_local_models=True,
        can_use_cloud_models=True,  # OpenAI only
        can_use_mcp=True,  # Limited to 1 server
        can_use_agentic=False,
        priority_support=False,
        priority_queue=False,
    ),
    
    SubscriptionTier.STARTER: TierLimits(
        max_conversations=10,
        max_files_per_conversation=20,
        max_total_storage_mb=500,
        queries_per_day=100,
        queries_per_month=2000,
        allowed_providers=["openai", "ollama", "lmstudio", "gemini"],
        max_mcp_servers=3,
        can_use_local_models=True,
        can_use_cloud_models=True,
        can_use_mcp=True,
        can_use_agentic=False,
        priority_support=False,
        priority_queue=False,
    ),
    
    SubscriptionTier.PRO: TierLimits(
        max_conversations=50,
        max_files_per_conversation=100,
        max_total_storage_mb=5000,
        queries_per_day=500,
        queries_per_month=10000,
        allowed_providers=["openai", "ollama", "lmstudio", "gemini", "claude", "copilot"],
        max_mcp_servers=10,
        can_use_local_models=True,
        can_use_cloud_models=True,
        can_use_mcp=True,
        can_use_agentic=True,  # n8n access
        priority_support=True,
        priority_queue=True,
    ),
    
    SubscriptionTier.ENTERPRISE: TierLimits(
        max_conversations=-1,  # Unlimited
        max_files_per_conversation=-1,
        max_total_storage_mb=-1,
        queries_per_day=-1,
        queries_per_month=-1,
        allowed_providers=["openai", "ollama", "lmstudio", "gemini", "claude", "copilot", "n8n", "mcp", "custom"],
        max_mcp_servers=-1,  # Unlimited
        can_use_local_models=True,
        can_use_cloud_models=True,
        can_use_mcp=True,
        can_use_agentic=True,
        priority_support=True,
        priority_queue=True,
    ),
}


def get_tier_limits(tier: SubscriptionTier) -> TierLimits:
    """Get limits for a subscription tier."""
    return TIER_CONFIGS.get(tier, TIER_CONFIGS[SubscriptionTier.FREE])


def is_provider_allowed(tier: SubscriptionTier, provider: str) -> bool:
    """Check if a provider is allowed for a tier."""
    limits = get_tier_limits(tier)
    return provider.lower() in [p.lower() for p in limits.allowed_providers]


def check_conversation_lock_needed(
    old_tier: SubscriptionTier,
    new_tier: SubscriptionTier,
    conversation_file_count: int,
    conversation_mcp_count: int,
    conversation_provider: str
) -> Dict[str, Any]:
    """
    Check if a conversation needs to be locked after a tier downgrade.
    
    Returns a dict with lock status and reasons.
    """
    new_limits = get_tier_limits(new_tier)
    
    lock_reasons = []
    
    # Check file count
    if new_limits.max_files_per_conversation != -1:
        if conversation_file_count > new_limits.max_files_per_conversation:
            lock_reasons.append(f"File count ({conversation_file_count}) exceeds limit ({new_limits.max_files_per_conversation})")
    
    # Check MCP servers
    if new_limits.max_mcp_servers != -1:
        if conversation_mcp_count > new_limits.max_mcp_servers:
            lock_reasons.append(f"MCP servers ({conversation_mcp_count}) exceed limit ({new_limits.max_mcp_servers})")
    
    # Check provider access
    if not is_provider_allowed(new_tier, conversation_provider):
        lock_reasons.append(f"Provider '{conversation_provider}' not available in {new_tier.value} tier")
    
    return {
        "locked": len(lock_reasons) > 0,
        "reasons": lock_reasons,
        "action_required": "Reduce files, MCP servers, or change provider to unlock" if lock_reasons else None
    }


# Feature flags for "Coming Soon" UI
FEATURE_STATUS = {
    "gemini": {"status": "coming_soon", "eta": "Q2 2026"},
    "claude": {"status": "coming_soon", "eta": "Q2 2026"},
    "copilot": {"status": "coming_soon", "eta": "Q3 2026"},
    "n8n": {"status": "coming_soon", "eta": "Q3 2026"},
    "mcp": {"status": "coming_soon", "eta": "Q2 2026"},
    "openai": {"status": "available", "eta": None},
    "ollama": {"status": "available", "eta": None},
    "lmstudio": {"status": "available", "eta": None},
}
