"""API Routes module."""

from .health_routes import router as health_router
from .transcript_routes import router as transcript_router
from .query_routes import router as query_router
from .auth_routes import router as auth_router

__all__ = [
    "health_router",
    "transcript_router",
    "query_router",
    "auth_router",
]