"""
LLM Routes - API endpoints for LLM provider management.

Provides endpoints to:
- List available LLM providers (OpenAI, Ollama, LM Studio)
- List coming soon providers (Gemini, Claude, Copilot, n8n, MCP)
- Get models for a specific provider
- Test provider connectivity
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from api.dependencies.auth import get_current_user
from models.user import User
from services.llm import (
    LLMProviderFactory, 
    LLMProviderConfig, 
    ProviderType,
    ProviderStatus,
    PROVIDER_METADATA,
    get_coming_soon_status
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ProviderInfo(BaseModel):
    """Information about an LLM provider."""
    provider: str
    name: str
    description: str
    available: bool
    status: str  # available, coming_soon, beta
    models: List[str]
    requires_api_key: bool
    is_local: bool
    endpoint: Optional[str] = None
    eta: Optional[str] = None  # For coming soon features


class ModelInfo(BaseModel):
    """Information about a specific model."""
    name: str
    provider: str
    description: Optional[str] = None


class TestConnectionRequest(BaseModel):
    """Request to test provider connection."""
    provider: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class TestConnectionResponse(BaseModel):
    """Response from connection test."""
    success: bool
    message: str
    models: Optional[List[str]] = None


# ============================================================================
# Routes
# ============================================================================

@router.get("/providers/", response_model=List[ProviderInfo])
async def list_providers(
    current_user: User = Depends(get_current_user)
):
    """
    List all LLM providers including available and coming soon.
    
    Returns information about:
    - Available: OpenAI, Ollama, LM Studio
    - Coming Soon: Gemini, Claude, Copilot, n8n, MCP
    """
    try:
        providers = await LLMProviderFactory.detect_available_providers()
        
        # All providers including coming soon
        all_providers = [
            # Available providers
            ProviderInfo(
                provider="openai",
                name="OpenAI",
                description="GPT-4, GPT-3.5 Turbo (cloud)",
                available=False,
                status="available",
                models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                requires_api_key=True,
                is_local=False
            ),
            ProviderInfo(
                provider="ollama",
                name="Ollama",
                description="Local LLMs (Llama, Mistral, etc.)",
                available=False,
                status="available",
                models=[],
                requires_api_key=False,
                is_local=True,
                endpoint="http://localhost:11434"
            ),
            ProviderInfo(
                provider="lmstudio",
                name="LM Studio",
                description="Local model runner",
                available=False,
                status="available",
                models=[],
                requires_api_key=False,
                is_local=True,
                endpoint="http://localhost:1234/v1"
            ),
            # Coming Soon providers
            ProviderInfo(
                provider="gemini",
                name="Google Gemini",
                description="Gemini Pro, Ultra (cloud)",
                available=False,
                status="coming_soon",
                models=["gemini-pro", "gemini-pro-vision", "gemini-ultra"],
                requires_api_key=True,
                is_local=False,
                eta="Q2 2026"
            ),
            ProviderInfo(
                provider="claude",
                name="Anthropic Claude",
                description="Claude 3 Opus, Sonnet, Haiku",
                available=False,
                status="coming_soon",
                models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                requires_api_key=True,
                is_local=False,
                eta="Q2 2026"
            ),
            ProviderInfo(
                provider="copilot",
                name="Microsoft Copilot",
                description="Azure OpenAI Service",
                available=False,
                status="coming_soon",
                models=["gpt-4", "gpt-35-turbo"],
                requires_api_key=True,
                is_local=False,
                eta="Q3 2026"
            ),
            ProviderInfo(
                provider="n8n",
                name="n8n Agentic",
                description="Workflow automation with AI",
                available=False,
                status="coming_soon",
                models=[],
                requires_api_key=True,
                is_local=False,
                eta="Q3 2026"
            ),
            ProviderInfo(
                provider="mcp",
                name="MCP Server",
                description="Model Context Protocol",
                available=False,
                status="coming_soon",
                models=[],
                requires_api_key=False,
                is_local=False,
                eta="Q2 2026"
            ),
        ]
        
        # Update with detected availability (only for implemented providers)
        for detected in providers:
            for provider in all_providers:
                if provider.provider == detected["provider"]:
                    provider.available = detected["available"]
                    if detected.get("models"):
                        provider.models = detected["models"]
                    if detected.get("endpoint"):
                        provider.endpoint = detected["endpoint"]
        
        return all_providers
        
    except Exception as e:
        logger.error(f"Failed to list providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{provider}/models/", response_model=List[str])
async def list_provider_models(
    provider: str,
    base_url: Optional[str] = Query(None, description="Custom endpoint URL"),
    current_user: User = Depends(get_current_user)
):
    """
    List available models for a specific provider.
    
    For local providers (Ollama, LM Studio), lists models currently installed.
    """
    try:
        # Create config based on provider
        if provider == "openai":
            config = LLMProviderConfig.openai()
        elif provider == "ollama":
            config = LLMProviderConfig.ollama(base_url=base_url or "http://localhost:11434")
        elif provider == "lmstudio":
            config = LLMProviderConfig.lmstudio(base_url=base_url or "http://localhost:1234/v1")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        llm_provider = LLMProviderFactory.create(config)
        models = await llm_provider.list_models()
        
        return models
        
    except HTTPException:
        raise
    except ConnectionError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Cannot connect to {provider}. Make sure it's running."
        )
    except Exception as e:
        logger.error(f"Failed to list models for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/providers/test/", response_model=TestConnectionResponse)
async def test_provider_connection(
    request: TestConnectionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Test connection to an LLM provider.
    
    Useful for verifying:
    - Ollama is running
    - LM Studio server is started
    - OpenAI API key is valid
    """
    try:
        provider_type = ProviderType(request.provider)
        
        config = LLMProviderConfig(
            provider_type=provider_type,
            model_name="test",
            base_url=request.base_url,
            api_key=request.api_key
        )
        
        llm_provider = LLMProviderFactory.create(config)
        available = await llm_provider.is_available()
        
        if available:
            models = await llm_provider.list_models()
            return TestConnectionResponse(
                success=True,
                message=f"Successfully connected to {request.provider}",
                models=models[:10]
            )
        else:
            return TestConnectionResponse(
                success=False,
                message=f"Cannot connect to {request.provider}. Please check if it's running.",
                models=None
            )
            
    except ValueError as e:
        return TestConnectionResponse(
            success=False,
            message=f"Invalid provider: {request.provider}",
            models=None
        )
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return TestConnectionResponse(
            success=False,
            message=str(e),
            models=None
        )


@router.get("/recommended-models/")
async def get_recommended_models(
    current_user: User = Depends(get_current_user)
):
    """
    Get recommended models for each provider.
    
    Returns curated list of popular/effective models.
    """
    return {
        "openai": [
            {"name": "gpt-4", "description": "Most capable, best for complex queries"},
            {"name": "gpt-4-turbo", "description": "Faster, good balance of speed and quality"},
            {"name": "gpt-3.5-turbo", "description": "Fast and cost-effective"},
        ],
        "ollama": [
            {"name": "llama3.2", "description": "Latest Llama, great all-around performance"},
            {"name": "llama3.1", "description": "Stable, well-tested"},
            {"name": "mistral", "description": "Fast, efficient for coding tasks"},
            {"name": "mixtral", "description": "Mixture of experts, powerful"},
            {"name": "codellama", "description": "Specialized for code"},
            {"name": "phi3", "description": "Small but capable Microsoft model"},
            {"name": "gemma2", "description": "Google's efficient model"},
        ],
        "lmstudio": [
            {"name": "Load any model in LM Studio", "description": "Use the model loaded in LM Studio"}
        ]
    }
