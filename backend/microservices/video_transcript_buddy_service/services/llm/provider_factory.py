"""
LLM Provider Factory - Create and manage LLM provider instances.
"""

import logging
from typing import Optional, Dict, List, Any

from .provider_interface import LLMProvider, LLMProviderConfig, ProviderType
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .lmstudio_provider import LMStudioProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory for creating and managing LLM providers.
    
    Supports caching of provider instances and auto-detection of available providers.
    """
    
    _instances: Dict[str, LLMProvider] = {}
    
    @classmethod
    def create(cls, config: LLMProviderConfig) -> LLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            config: Provider configuration
            
        Returns:
            LLMProvider instance
        """
        provider_map = {
            ProviderType.OPENAI: OpenAIProvider,
            ProviderType.OLLAMA: OllamaProvider,
            ProviderType.LMSTUDIO: LMStudioProvider,
            ProviderType.CUSTOM: LMStudioProvider,  # Custom uses OpenAI-compatible API
        }
        
        provider_class = provider_map.get(config.provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {config.provider_type}")
        
        return provider_class(config)
    
    @classmethod
    def get_or_create(cls, config: LLMProviderConfig) -> LLMProvider:
        """
        Get cached provider or create new one.
        
        Args:
            config: Provider configuration
            
        Returns:
            Cached or new LLMProvider instance
        """
        cache_key = f"{config.provider_type}:{config.model_name}:{config.base_url or 'default'}"
        
        if cache_key not in cls._instances:
            cls._instances[cache_key] = cls.create(config)
        
        return cls._instances[cache_key]
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached provider instances."""
        cls._instances.clear()
    
    @classmethod
    async def detect_available_providers(cls) -> List[Dict[str, Any]]:
        """
        Detect which LLM providers are available.
        
        Returns:
            List of available provider info dicts
        """
        available = []
        
        # Check OpenAI
        try:
            from config.settings import settings
            if settings.OPENAI_API_KEY:
                openai_config = LLMProviderConfig.openai()
                openai_provider = cls.create(openai_config)
                if await openai_provider.is_available():
                    models = await openai_provider.list_models()
                    available.append({
                        "provider": ProviderType.OPENAI.value,
                        "name": "OpenAI",
                        "description": "OpenAI GPT models (cloud)",
                        "available": True,
                        "models": models[:10],  # Limit to top 10
                        "requires_api_key": True,
                        "is_local": False
                    })
        except Exception as e:
            logger.debug(f"OpenAI not available: {e}")
        
        # Check Ollama
        try:
            ollama_config = LLMProviderConfig.ollama()
            ollama_provider = cls.create(ollama_config)
            if await ollama_provider.is_available():
                models = await ollama_provider.list_models()
                available.append({
                    "provider": ProviderType.OLLAMA.value,
                    "name": "Ollama",
                    "description": "Local LLM with Ollama (free, private)",
                    "available": True,
                    "models": models,
                    "requires_api_key": False,
                    "is_local": True,
                    "endpoint": ollama_config.base_url
                })
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
        
        # Check LM Studio
        try:
            lmstudio_config = LLMProviderConfig.lmstudio()
            lmstudio_provider = cls.create(lmstudio_config)
            if await lmstudio_provider.is_available():
                models = await lmstudio_provider.list_models()
                available.append({
                    "provider": ProviderType.LMSTUDIO.value,
                    "name": "LM Studio",
                    "description": "Local LLM with LM Studio (free, private)",
                    "available": True,
                    "models": models,
                    "requires_api_key": False,
                    "is_local": True,
                    "endpoint": lmstudio_config.base_url
                })
        except Exception as e:
            logger.debug(f"LM Studio not available: {e}")
        
        return available


def get_llm_provider(
    provider_type: str = "openai",
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> LLMProvider:
    """
    Convenience function to get an LLM provider.
    
    Args:
        provider_type: Type of provider ('openai', 'ollama', 'lmstudio')
        model_name: Model to use (defaults vary by provider)
        base_url: Custom endpoint URL
        api_key: API key (for OpenAI)
        
    Returns:
        Configured LLMProvider instance
    """
    # Set default models per provider
    default_models = {
        "openai": "gpt-4",
        "ollama": "llama3.2",
        "lmstudio": "local-model"
    }
    
    model = model_name or default_models.get(provider_type, "default")
    
    config = LLMProviderConfig(
        provider_type=ProviderType(provider_type),
        model_name=model,
        base_url=base_url,
        api_key=api_key
    )
    
    return LLMProviderFactory.get_or_create(config)
