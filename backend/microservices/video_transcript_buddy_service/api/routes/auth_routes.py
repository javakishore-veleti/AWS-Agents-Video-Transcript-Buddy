"""
Auth Routes - REST endpoints for authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.auth_service import AuthService
from api.models.request_models import RegisterRequest, LoginRequest, RefreshTokenRequest
from api.models.response_models import AuthResponse, TokenResponse
from common.exceptions import ValidationException, AuthenticationException

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with FREE tier"
)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Min 8 characters
    - **full_name**: Optional full name
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        # Auto login after registration
        tokens = auth_service.login(request.email, request.password)
        
        return AuthResponse(
            success=True,
            message="Registration successful",
            data=tokens
        )
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate and get access tokens"
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    - **email**: Registered email
    - **password**: Account password
    """
    try:
        auth_service = AuthService(db)
        tokens = auth_service.login(
            email=request.email,
            password=request.password
        )
        
        return AuthResponse(
            success=True,
            message="Login successful",
            data=tokens
        )
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.to_dict()
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token.
    
    - **refresh_token**: Valid refresh token
    """
    try:
        auth_service = AuthService(db)
        tokens = auth_service.refresh_tokens(request.refresh_token)
        
        return TokenResponse(
            success=True,
            message="Token refreshed",
            data=tokens
        )
    
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.to_dict()
        )