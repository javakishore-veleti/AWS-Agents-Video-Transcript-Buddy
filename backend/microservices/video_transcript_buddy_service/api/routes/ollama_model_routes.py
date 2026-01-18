"""
Ollama Model Routes - REST endpoints for Ollama model management.

Endpoints:
- POST /discover - Discover models from Ollama (npm run ollama:discover)
- GET / - List all discovered models
- GET /enabled - List enabled & installed models (for chat UI)
- PUT /{model_id}/toggle - Enable/disable a model
- GET /conversation/{conversation_id} - Get models for a conversation
- POST /conversation/{conversation_id}/add - Add a model to a conversation
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from config.database import get_db
from services.ollama_model_service import ollama_model_service
from api.dependencies.auth import get_current_user
from api.dependencies.id_encryption import get_id_encryptor
from utils.id_encryption import UserIDEncryptor
from models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/discover",
    summary="Discover Ollama models",
    description="Discover installed models from Ollama. Called by `npm run ollama:discover`."
)
async def discover_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Discover and store Ollama models.
    
    - Fetches models from Ollama API
    - Stores NEW models in database (never deletes existing)
    - Updates last_seen_at for existing models
    - Marks uninstalled models as is_installed=False
    """
    result = await ollama_model_service.discover_models(db)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result.get("error", "Discovery failed")
        )
    
    return result


@router.get(
    "/",
    summary="List all discovered models",
    description="Get all Ollama models ever discovered on this system"
)
async def list_models(
    include_disabled: bool = Query(False, description="Include disabled models"),
    installed_only: bool = Query(False, description="Only installed models"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all discovered Ollama models."""
    models = ollama_model_service.get_all_models(
        db, 
        include_disabled=include_disabled,
        installed_only=installed_only
    )
    
    return {
        "success": True,
        "models": models,
        "total": len(models)
    }


@router.get(
    "/enabled",
    summary="List enabled models",
    description="Get enabled and installed models (for chat UI model selector)"
)
async def list_enabled_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get only enabled and installed models for the chat UI."""
    models = ollama_model_service.get_enabled_models(db)
    
    return {
        "success": True,
        "models": models,
        "total": len(models)
    }


@router.put(
    "/{model_id}/toggle",
    summary="Toggle model enabled status",
    description="Enable or disable a model"
)
async def toggle_model(
    model_id: str,
    enabled: Optional[bool] = Query(None, description="Set enabled state (omit to toggle)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle or set a model's enabled status.
    
    - If `enabled` is omitted, toggles current state
    - If `enabled` is provided, sets to that value
    """
    result = ollama_model_service.toggle_model(db, model_id, enabled)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Toggle failed")
        )
    
    return result


@router.get(
    "/conversation/{conversation_id}",
    summary="Get conversation models",
    description="Get models available for a specific conversation"
)
async def get_conversation_models(
    conversation_id: str,
    include_new: bool = Query(True, description="Include newly discovered models"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
):
    """
    Get models for a conversation.
    
    Returns:
    - Models linked when conversation was created (is_original=True)
    - Optionally, new models discovered since (is_new=True)
    """
    # Decrypt conversation ID
    try:
        decrypted_conv_id = encryptor.decrypt(conversation_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )
    
    models = ollama_model_service.get_conversation_models(
        db, 
        str(decrypted_conv_id),
        include_new=include_new
    )
    
    return {
        "success": True,
        "models": models,
        "total": len(models),
        "original_count": sum(1 for m in models if m.get("is_original")),
        "new_count": sum(1 for m in models if m.get("is_new"))
    }


@router.post(
    "/conversation/{conversation_id}/add/{model_id}",
    summary="Add model to conversation",
    description="Add a newly discovered model to an existing conversation"
)
async def add_model_to_conversation(
    conversation_id: str,
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    encryptor: UserIDEncryptor = Depends(get_id_encryptor)
):
    """Add a model to a conversation (for newly discovered models)."""
    # Decrypt conversation ID
    try:
        decrypted_conv_id = encryptor.decrypt(conversation_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )
    
    result = ollama_model_service.add_model_to_conversation(
        db, 
        str(decrypted_conv_id),
        model_id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Failed to add model")
        )
    
    return result
