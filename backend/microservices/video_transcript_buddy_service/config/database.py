"""
Database Connection - SQLAlchemy setup for SQLite (local) and PostgreSQL (production).

Usage:
    from config.database import get_db, engine, Base
    
    # In FastAPI dependency
    def get_current_user(db: Session = Depends(get_db)):
        ...
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
"""

import os
import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import StaticPool, QueuePool

from config.settings import settings

logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()


def get_engine():
    """
    Create SQLAlchemy engine based on configuration.
    
    - SQLite: Uses StaticPool for thread safety, enables foreign keys
    - PostgreSQL: Uses QueuePool with connection pooling
    """
    database_uri = settings.database_uri
    
    if settings.is_sqlite:
        # SQLite configuration
        logger.info(f"Using SQLite database: {settings.SQLITE_DATABASE_PATH}")
        
        # Ensure directory exists
        db_dir = os.path.dirname(settings.SQLITE_DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        engine = create_engine(
            database_uri,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG
        )
        
        # Enable foreign key support for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        return engine
    
    else:
        # PostgreSQL configuration
        logger.info("Using PostgreSQL database")
        
        engine = create_engine(
            database_uri,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=True,  # Verify connections before use
            echo=settings.DEBUG
        )
        
        return engine


# Create engine instance
engine = get_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions (use outside FastAPI).
    
    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    
    Call this at application startup.
    """
    # Import all models to register them with Base
    from models import user, subscription, usage  # noqa: F401
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db():
    """
    Drop all tables - use with caution!
    
    Only for testing/development.
    """
    logger.warning("Dropping all database tables!")
    Base.metadata.drop_all(bind=engine)
