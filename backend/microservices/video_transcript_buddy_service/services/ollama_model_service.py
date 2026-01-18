"""
Ollama Model Service - Service for discovering and managing Ollama models.

Handles:
- Discovering installed models from Ollama API
- Storing discovered models in database (never deletes, only adds)
- Linking models to conversations at creation time
- Enabling/disabling models for user preference
"""

import logging
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models.ollama_model import OllamaModel, RECOMMENDED_MODELS, conversation_models
from models.conversation import Conversation
from config import settings

logger = logging.getLogger(__name__)

# Ollama API endpoints
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"


class OllamaModelService:
    """Service for managing Ollama models."""
    
    def __init__(self):
        """Initialize the service."""
        pass
    
    async def discover_models(self, db: Session) -> Dict[str, Any]:
        """
        Discover models from Ollama and store new ones in database.
        
        This is called by `npm run ollama:discover` command.
        Models are NEVER deleted - only new ones are added.
        
        Returns:
            Dict with discovery results: new models found, total models, etc.
        """
        try:
            # Fetch models from Ollama API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(OLLAMA_TAGS_URL)
                response.raise_for_status()
                data = response.json()
            
            ollama_models = data.get("models", [])
            logger.info(f"Ollama returned {len(ollama_models)} installed models")
            
            new_models = []
            updated_models = []
            
            for model_data in ollama_models:
                model_name = model_data.get("name", "")
                if not model_name:
                    continue
                
                # Check if model already exists
                existing = db.query(OllamaModel).filter(
                    OllamaModel.name == model_name
                ).first()
                
                if existing:
                    # Update last_seen_at and mark as installed
                    existing.last_seen_at = datetime.utcnow()
                    existing.is_installed = True
                    existing.digest = model_data.get("digest")
                    existing.size_bytes = model_data.get("size")
                    updated_models.append(model_name)
                else:
                    # Extract model details
                    details = model_data.get("details", {})
                    
                    # Check if it's a recommended model
                    base_name = model_name.split(":")[0]
                    is_recommended = base_name in RECOMMENDED_MODELS
                    
                    # Create new model record
                    new_model = OllamaModel(
                        name=model_name,
                        model_family=details.get("family"),
                        parameter_size=details.get("parameter_size"),
                        quantization=details.get("quantization_level"),
                        size_bytes=model_data.get("size"),
                        digest=model_data.get("digest"),
                        is_installed=True,
                        is_enabled=True,
                        is_recommended=is_recommended,
                        discovered_at=datetime.utcnow(),
                        last_seen_at=datetime.utcnow()
                    )
                    
                    db.add(new_model)
                    new_models.append(model_name)
                    logger.info(f"Discovered new model: {model_name}")
            
            # Mark models not seen as possibly uninstalled (but don't delete!)
            all_seen_names = [m.get("name") for m in ollama_models]
            not_seen = db.query(OllamaModel).filter(
                OllamaModel.name.notin_(all_seen_names),
                OllamaModel.is_installed == True
            ).all()
            
            for model in not_seen:
                model.is_installed = False
                logger.info(f"Model no longer installed: {model.name}")
            
            db.commit()
            
            return {
                "success": True,
                "new_models": new_models,
                "new_count": len(new_models),
                "updated_models": updated_models,
                "updated_count": len(updated_models),
                "total_installed": len(ollama_models),
                "message": f"Discovered {len(new_models)} new model(s), updated {len(updated_models)} existing"
            }
            
        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama - is it running?")
            return {
                "success": False,
                "error": "Cannot connect to Ollama. Make sure it's running: `npm run ollama:start`",
                "new_count": 0,
                "updated_count": 0
            }
        except Exception as e:
            logger.error(f"Model discovery failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "new_count": 0,
                "updated_count": 0
            }
    
    def get_all_models(
        self, 
        db: Session,
        include_disabled: bool = False,
        installed_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all discovered models.
        
        Args:
            db: Database session
            include_disabled: Include disabled models
            installed_only: Only return currently installed models
            
        Returns:
            List of model dictionaries
        """
        query = db.query(OllamaModel)
        
        if not include_disabled:
            query = query.filter(OllamaModel.is_enabled == True)
        
        if installed_only:
            query = query.filter(OllamaModel.is_installed == True)
        
        # Order: recommended first, then by name
        models = query.order_by(
            OllamaModel.is_recommended.desc(),
            OllamaModel.is_installed.desc(),
            OllamaModel.name
        ).all()
        
        return [m.to_dict() for m in models]
    
    def get_enabled_models(self, db: Session) -> List[Dict[str, Any]]:
        """Get only enabled and installed models (for chat UI)."""
        return self.get_all_models(db, include_disabled=False, installed_only=True)
    
    def toggle_model(
        self, 
        db: Session, 
        model_id: str, 
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Toggle or set model enabled status.
        
        Args:
            db: Database session
            model_id: Model ID
            enabled: If None, toggle. If bool, set to that value.
            
        Returns:
            Updated model dict
        """
        model = db.query(OllamaModel).filter(OllamaModel.id == model_id).first()
        
        if not model:
            return {"success": False, "error": "Model not found"}
        
        if enabled is None:
            model.is_enabled = not model.is_enabled
        else:
            model.is_enabled = enabled
        
        db.commit()
        db.refresh(model)
        
        return {
            "success": True,
            "model": model.to_dict(),
            "message": f"Model {model.name} {'enabled' if model.is_enabled else 'disabled'}"
        }
    
    def link_models_to_conversation(
        self, 
        db: Session, 
        conversation_id: str
    ) -> int:
        """
        Link all currently enabled & installed models to a conversation.
        
        Called when a conversation is created to snapshot available models.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            Number of models linked
        """
        # Get all enabled and installed models
        models = db.query(OllamaModel).filter(
            OllamaModel.is_enabled == True,
            OllamaModel.is_installed == True
        ).all()
        
        # Link each to the conversation
        for model in models:
            # Check if already linked
            existing = db.execute(
                conversation_models.select().where(
                    conversation_models.c.conversation_id == conversation_id,
                    conversation_models.c.model_id == model.id
                )
            ).first()
            
            if not existing:
                db.execute(
                    conversation_models.insert().values(
                        conversation_id=conversation_id,
                        model_id=model.id
                    )
                )
        
        db.commit()
        logger.info(f"Linked {len(models)} models to conversation {conversation_id}")
        return len(models)
    
    def get_conversation_models(
        self, 
        db: Session, 
        conversation_id: str,
        include_new: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get models available for a conversation.
        
        Returns models that were linked when conversation was created,
        plus optionally any new models discovered since then.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            include_new: Also include newly discovered models not yet linked
            
        Returns:
            List of model dictionaries with 'is_original' flag
        """
        # Get originally linked models
        original_query = db.query(OllamaModel).join(
            conversation_models,
            conversation_models.c.model_id == OllamaModel.id
        ).filter(
            conversation_models.c.conversation_id == conversation_id,
            OllamaModel.is_enabled == True
        )
        
        original_models = original_query.all()
        original_ids = {m.id for m in original_models}
        
        result = []
        for model in original_models:
            model_dict = model.to_dict()
            model_dict["is_original"] = True  # Was available at conversation creation
            model_dict["is_new"] = False
            result.append(model_dict)
        
        # Optionally add new models discovered after conversation creation
        if include_new:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                new_models = db.query(OllamaModel).filter(
                    OllamaModel.id.notin_(original_ids),
                    OllamaModel.is_enabled == True,
                    OllamaModel.is_installed == True,
                    OllamaModel.discovered_at > conversation.created_at
                ).all()
                
                for model in new_models:
                    model_dict = model.to_dict()
                    model_dict["is_original"] = False
                    model_dict["is_new"] = True  # Discovered after conversation
                    result.append(model_dict)
        
        # Sort: recommended first, then original before new, then by name
        result.sort(key=lambda m: (
            not m.get("is_recommended", False),
            not m.get("is_original", True),
            m.get("name", "")
        ))
        
        return result
    
    def add_model_to_conversation(
        self,
        db: Session,
        conversation_id: str,
        model_id: str
    ) -> Dict[str, Any]:
        """
        Add a newly discovered model to an existing conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            model_id: Model ID to add
            
        Returns:
            Success status
        """
        # Verify model exists and is enabled
        model = db.query(OllamaModel).filter(
            OllamaModel.id == model_id,
            OllamaModel.is_enabled == True
        ).first()
        
        if not model:
            return {"success": False, "error": "Model not found or disabled"}
        
        # Check if already linked
        existing = db.execute(
            conversation_models.select().where(
                conversation_models.c.conversation_id == conversation_id,
                conversation_models.c.model_id == model_id
            )
        ).first()
        
        if existing:
            return {"success": True, "message": "Model already linked"}
        
        # Add link
        db.execute(
            conversation_models.insert().values(
                conversation_id=conversation_id,
                model_id=model_id
            )
        )
        db.commit()
        
        return {
            "success": True,
            "message": f"Added {model.name} to conversation",
            "model": model.to_dict()
        }


# Singleton instance
ollama_model_service = OllamaModelService()
