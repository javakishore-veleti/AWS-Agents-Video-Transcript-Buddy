"""
Conversation Service - Business logic for conversation/collection management.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from models.conversation import Conversation
from models.user import User
from models.subscription import get_tier_limits
from common.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation operations with tier-based validation."""
    
    def create_conversation(
        self,
        db: Session,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        llm_temperature: float = 0.7,
        llm_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            db: Database session
            user_id: ID of the user
            name: Optional name (auto-generated if not provided)
            description: Optional description
            llm_provider: LLM provider (openai, ollama, lmstudio)
            llm_model: Model name
            llm_temperature: Temperature for generation
            llm_base_url: Custom endpoint URL for local models
            
        Returns:
            Dict with conversation details
            
        Raises:
            ValidationException: If user exceeds tier limits
        """
        # Get user and tier limits
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValidationException("User not found")
        
        tier_limits = get_tier_limits(user.tier)
        
        # Check conversation limit
        current_count = db.query(Conversation).filter(Conversation.user_id == user_id).count()
        if tier_limits.max_conversations != -1 and current_count >= tier_limits.max_conversations:
            raise ValidationException(
                f"Conversation limit reached for {user.tier} tier. "
                f"Maximum: {tier_limits.max_conversations}. "
                f"Please upgrade your subscription or delete existing conversations."
            )
        
        # Create conversation
        conversation = Conversation(
            name=name or Conversation.generate_default_name(),
            user_id=user_id,
            description=description,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_temperature=llm_temperature,
            llm_base_url=llm_base_url
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Link available Ollama models to this conversation
        # This snapshots what models are available at conversation creation time
        try:
            from services.ollama_model_service import ollama_model_service
            models_linked = ollama_model_service.link_models_to_conversation(db, conversation.id)
            logger.info(f"Linked {models_linked} Ollama models to conversation {conversation.id}")
        except Exception as e:
            logger.warning(f"Could not link Ollama models to conversation: {e}")
            # Non-fatal - conversation still works without linked models
        
        logger.info(f"Created conversation '{conversation.name}' for user {user_id}")
        
        return conversation.to_dict()
    
    def list_conversations(
        self,
        db: Session,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """List all conversations for a user."""
        conversations = db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.last_activity_at.desc())\
            .all()
        
        return [conv.to_dict() for conv in conversations]
    
    def get_conversation(
        self,
        db: Session,
        conversation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get a specific conversation."""
        conversation = db.query(Conversation)\
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)\
            .first()
        
        if not conversation:
            raise ValidationException("Conversation not found")
        
        return conversation.to_dict()
    
    def update_conversation(
        self,
        db: Session,
        conversation_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_temperature: Optional[float] = None,
        llm_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update conversation details and LLM settings."""
        conversation = db.query(Conversation)\
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)\
            .first()
        
        if not conversation:
            raise ValidationException("Conversation not found")
        
        if name:
            conversation.name = name
        if description is not None:
            conversation.description = description
        
        # Update LLM settings if provided
        if llm_provider is not None:
            conversation.llm_provider = llm_provider
        if llm_model is not None:
            conversation.llm_model = llm_model
        if llm_temperature is not None:
            conversation.llm_temperature = llm_temperature
        if llm_base_url is not None:
            conversation.llm_base_url = llm_base_url
        
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Updated conversation {conversation_id}")
        
        return conversation.to_dict()
    
    def delete_conversation(
        self,
        db: Session,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Delete a conversation and all its transcripts."""
        conversation = db.query(Conversation)\
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)\
            .first()
        
        if not conversation:
            raise ValidationException("Conversation not found")
        
        db.delete(conversation)
        db.commit()
        
        logger.info(f"Deleted conversation {conversation_id} and its {conversation.file_count} files")
        
        return True
    
    def validate_downgrade(
        self,
        db: Session,
        user_id: str,
        new_tier: str
    ) -> Dict[str, Any]:
        """
        Validate if user can downgrade to new tier.
        
        Returns:
            Dict with validation result and required actions
        """
        current_conversations = db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .all()
        
        new_tier_limits = get_tier_limits(new_tier)
        
        # Check conversation count
        current_count = len(current_conversations)
        max_allowed = new_tier_limits.max_conversations
        
        if max_allowed != -1 and current_count > max_allowed:
            excess_count = current_count - max_allowed
            return {
                "can_downgrade": False,
                "reason": "Too many conversations",
                "current_count": current_count,
                "max_allowed": max_allowed,
                "excess_count": excess_count,
                "action_required": f"Please delete {excess_count} conversation(s) before downgrading to {new_tier} tier"
            }
        
        # Check files per conversation
        violations = []
        max_files = new_tier_limits.max_files_per_conversation
        
        if max_files != -1:
            for conv in current_conversations:
                if conv.file_count > max_files:
                    violations.append({
                        "conversation_id": conv.id,
                        "conversation_name": conv.name,
                        "current_files": conv.file_count,
                        "max_allowed": max_files,
                        "excess": conv.file_count - max_files
                    })
        
        if violations:
            return {
                "can_downgrade": False,
                "reason": "Too many files in conversations",
                "violations": violations,
                "action_required": f"Some conversations exceed the {max_files} file limit for {new_tier} tier"
            }
        
        return {
            "can_downgrade": True,
            "message": f"You can safely downgrade to {new_tier} tier"
        }
    
    def update_conversation_stats(
        self,
        db: Session,
        conversation_id: str,
        file_count_delta: int = 0,
        query_count_delta: int = 0,
        size_delta_bytes: int = 0
    ):
        """Update conversation statistics."""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        
        if conversation:
            conversation.file_count += file_count_delta
            conversation.query_count += query_count_delta
            conversation.total_size_bytes += size_delta_bytes
            conversation.last_activity_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()
            db.commit()
