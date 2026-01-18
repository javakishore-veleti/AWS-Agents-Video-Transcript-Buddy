"""API Routes module."""

from .health_routes import router as health_router
from .transcript_routes import router as transcript_router
from .conversation_routes import router as conversation_router
from .query_routes import router as query_router
from .auth_routes import router as auth_router
from .usage_routes import router as usage_router
from .admin_routes import router as admin_router

__all__ = [
    "health_router",
    "transcript_router",
    "conversation_router",
    "query_router",
    "auth_router",
    "usage_router",
    "admin_router",
]