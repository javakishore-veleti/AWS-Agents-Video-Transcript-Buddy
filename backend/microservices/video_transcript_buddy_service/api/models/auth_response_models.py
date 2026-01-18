"""
Auth Response Models - Pydantic models for auth API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AuthResponse(BaseModel):
    """Response model for auth operations (register/login)."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Auth data with tokens and user info"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Login successful",
                "data": {
                    "access_token": "eyJ...",
                    "refresh_token": "eyJ...",
                    "token_type": "bearer",
                    "user": {
                        "id": "uuid-here",
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "tier": "FREE"
                    }
                }
            }
        }


class TokenResponse(BaseModel):
    """Response model for token refresh."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, str]] = Field(
        default=None,
        description="New access token"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Token refreshed",
                "data": {
                    "access_token": "eyJ...",
                    "token_type": "bearer"
                }
            }
        }


class UserResponse(BaseModel):
    """Response model for user info."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="User information"
    )