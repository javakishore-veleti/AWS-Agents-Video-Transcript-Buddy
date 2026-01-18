"""
Conversation Routes - REST endpoints for conversation management.
With per-user ID encryption for secure API communication.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.database import get_db
from services.conversation_service import ConversationService
from api.dependencies.auth import get_current_user
from api.dependencies.id_encryption import get_id_encryptor
from utils.id_encryption import UserIDEncryptor
from models.user import User
from common.exceptions import ValidationException

router = APIRouter()
conversation_service = ConversationService()


# ID fields to encrypt in responses
ENCRYPTED_ID_FIELDS = ['id', 'user_id']


def encrypt_conversation_response(data: dict, encryptor: UserIDEncryptor) -> dict:
    """Encrypt ID fields in conversation response."""
    return encryptor.encrypt_dict(data, ENCRYPTED_ID_FIELDS)


def encrypt_conversation_list(data_list: list, encryptor: UserIDEncryptor) -> list:
    """Encrypt ID fields in list of conversations."""
    return [encrypt_conversation_response(item, encryptor) for item in data_list]


# Request/Response Models
class CreateConversationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    # LLM Settings
    llm_provider: Optional[str] = "openai"
    llm_model: Optional[str] = "gpt-4"
    llm_temperature: Optional[float] = 0.7
    llm_base_url: Optional[str] = None


class UpdateConversationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    # LLM Settings
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None
    llm_base_url: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    name: str
    user_id: str
    description: Optional[str]
    # LLM Settings
    llm_provider: Optional[str] = "openai"
    llm_model: Optional[str] = "gpt-4"
    llm_temperature: Optional[float] = 0.7
    llm_base_url: Optional[str] = None
    # Statistics
    file_count: int
    query_count: int
    total_size_mb: float
    created_at: str
    updated_at: str
    last_activity_at: str


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation"
)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
):
    """
    Create a new conversation workspace.
    
    - **name**: Optional name (auto-generated from datetime if not provided)
    - **description**: Optional description
    - **llm_provider**: LLM provider (openai, ollama, lmstudio)
    - **llm_model**: Model name for the provider
    - **llm_temperature**: Temperature for generation (0.0 - 1.0)
    - **llm_base_url**: Custom endpoint URL for local models
    """
    try:
        result = conversation_service.create_conversation(
            db=db,
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model,
            llm_temperature=request.llm_temperature,
            llm_base_url=request.llm_base_url
        )
        return encrypt_conversation_response(result, encryptor)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[ConversationResponse],
    summary="List all conversations"
)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
):
    """List all conversations for the current user."""
    conversations = conversation_service.list_conversations(
        db=db,
        user_id=current_user.id
    )
    return encrypt_conversation_list(conversations, encryptor)


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation details"
)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
):
    """Get details of a specific conversation."""
    try:
        # Decrypt the conversation ID from request
        decrypted_id = encryptor.decrypt(conversation_id)
        
        conversation = conversation_service.get_conversation(
            db=db,
            conversation_id=decrypted_id,
            user_id=current_user.id
        )
        return encrypt_conversation_response(conversation, encryptor)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired conversation ID"
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Update conversation"
)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
):
    """Update conversation name, description, or LLM settings."""
    try:
        # Decrypt the conversation ID from request
        decrypted_id = encryptor.decrypt(conversation_id)
        
        result = conversation_service.update_conversation(
            db=db,
            conversation_id=decrypted_id,
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model,
            llm_temperature=request.llm_temperature,
            llm_base_url=request.llm_base_url
        )
        return encrypt_conversation_response(result, encryptor)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired conversation ID"
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete conversation"
)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
):
    """Delete a conversation and all its transcripts."""
    try:
        # Decrypt the conversation ID from request
        decrypted_id = encryptor.decrypt(conversation_id)
        
        conversation_service.delete_conversation(
            db=db,
            conversation_id=decrypted_id,
            user_id=current_user.id
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired conversation ID"
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/validate-downgrade",
    summary="Validate subscription downgrade"
)
async def validate_downgrade(
    new_tier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user can downgrade to a lower tier.
    Returns validation result and required actions.
    """
    result = conversation_service.validate_downgrade(
        db=db,
        user_id=current_user.id,
        new_tier=new_tier
    )
    return result
