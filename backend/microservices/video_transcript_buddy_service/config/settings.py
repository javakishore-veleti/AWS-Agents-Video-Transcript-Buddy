"""
Application Settings - Configuration management using environment variables.

Usage:
    from config import settings
    print(settings.AWS_REGION)

Note: 
    - AWS credentials are loaded from AWS profile (not stored in .env)
    - OPENAI_API_KEY should be set as system environment variable
    - DATABASE_URL defaults to SQLite for local dev, set for PostgreSQL in production
"""

import os
from typing import Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Settings
    APP_NAME: str = "Video Transcript Buddy Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # -----------------------------------------------------------------------------
    # Database Settings (SQLite local / PostgreSQL production)
    # -----------------------------------------------------------------------------
    # If DATABASE_URL is set, use PostgreSQL; otherwise default to SQLite
    DATABASE_URL: Optional[str] = None
    SQLITE_DATABASE_PATH: str = "./data/transcriptquery.db"
    
    # Database pool settings (for PostgreSQL)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    @property
    def database_uri(self) -> str:
        """Get the database URI - PostgreSQL if configured, else SQLite."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"sqlite:///{self.SQLITE_DATABASE_PATH}"
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite."""
        return self.DATABASE_URL is None
    
    # -----------------------------------------------------------------------------
    # AWS Settings (uses AWS profile - no keys stored!)
    # -----------------------------------------------------------------------------
    AWS_PROFILE: str = "video-transcript-buddy"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # S3 Settings
    S3_BUCKET_NAME: Optional[str] = "video-transcript-buddy-bucket"
    S3_TRANSCRIPT_FOLDER: str = "transcripts"
    S3_ARCHIVE_FOLDER: str = "archive"
    
    # -----------------------------------------------------------------------------
    # OpenAI Settings
    # -----------------------------------------------------------------------------
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Vector Store Settings
    VECTOR_STORE_TYPE: str = "local"
    VECTOR_STORE_PATH: str = "./data/vectors"
    VECTOR_CHUNK_SIZE: int = 1000
    VECTOR_CHUNK_OVERLAP: int = 200
    
    # AgentCore Settings
    AGENTCORE_ENABLED: bool = False
    AGENTCORE_ENDPOINT_URL: Optional[str] = None
    
    # -----------------------------------------------------------------------------
    # Authentication Settings
    # -----------------------------------------------------------------------------
    SECRET_KEY: str = "change-this-in-production-use-strong-random-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:4200,http://127.0.0.1:4200"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Fallback to system environment for OPENAI_API_KEY if not set
        if not self.OPENAI_API_KEY:
            self.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()