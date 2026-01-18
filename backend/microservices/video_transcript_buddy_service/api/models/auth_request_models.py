"""
Auth Request Models - Pydantic models for auth API requests.
"""

from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["user@example.com"]
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password (8-72 characters, bcrypt limit)",
        examples=["SecurePass123!"]
    )
    
    full_name: str | None = Field(
        default=None,
        max_length=255,
        description="Optional full name",
        examples=["John Doe"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["user@example.com"]
    )
    
    password: str = Field(
        ...,
        description="Account password",
        examples=["securepassword123"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    
    refresh_token: str = Field(
        ...,
        description="Valid refresh token"
    )