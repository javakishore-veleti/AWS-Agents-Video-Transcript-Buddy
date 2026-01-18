"""
Database Models - SQLAlchemy ORM models for users, subscriptions, usage tracking, and conversations.
"""

from .user import User
from .subscription import TierName, TierLimits, Subscription, SubscriptionStatus, TIERS, get_tier_limits
from .usage import UsageType, UsageRecord
from .conversation import Conversation
from .transcript import Transcript
from .mcp_server import MCPServer, MCPServerStatus, ConversationMCPServer
from .ollama_model import OllamaModel, conversation_models, RECOMMENDED_MODELS

__all__ = [
    "User",
    "TierName",
    "TierLimits",
    "Subscription",
    "SubscriptionStatus",
    "TIERS",
    "get_tier_limits",
    "UsageType",
    "UsageRecord",
    "Conversation",
    "Transcript",
    # MCP (Coming Soon)
    "MCPServer",
    "MCPServerStatus",
    "ConversationMCPServer",
    # Ollama Models
    "OllamaModel",
    "conversation_models",
    "RECOMMENDED_MODELS",
]