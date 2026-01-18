"""
LM Studio Provider - Implementation for LM Studio local server.

LM Studio provides an OpenAI-compatible API at http://localhost:1234/v1
by default, making it easy to use as a drop-in replacement.
"""

import logging
from typing import List, Optional, Dict, Any

from .provider_interface import LLMProvider, LLMProviderConfig, LLMResponse, ProviderType

logger = logging.getLogger(__name__)

# Default LM Studio endpoint (OpenAI-compatible)
DEFAULT_LMSTUDIO_URL = "http://localhost:1234/v1"


class LMStudioProvider(LLMProvider):
    """LM Studio local LLM provider implementation."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.LMSTUDIO
    
    @property
    def base_url(self) -> str:
        """Get LM Studio base URL."""
        return self.config.base_url or DEFAULT_LMSTUDIO_URL
    
    def _get_client(self):
        """Lazy-load OpenAI client pointed at LM Studio."""
        if self._client is None:
            try:
                from openai import OpenAI
                
                # LM Studio uses OpenAI-compatible API
                # No API key needed for local server
                self._client = OpenAI(
                    base_url=self.base_url,
                    api_key="lm-studio"  # Placeholder, not validated
                )
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        return self._client
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response using LM Studio."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return await self.generate_chat(messages, temperature, max_tokens)
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a chat response using LM Studio."""
        try:
            client = self._get_client()
            
            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens
            )
            
            choice = response.choices[0]
            
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model if response.model else self.config.model_name,
                provider=self.provider_type,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                } if response.usage else None,
                finish_reason=choice.finish_reason,
                raw_response=response
            )
        except Exception as e:
            logger.error(f"LM Studio generation failed: {e}")
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding using LM Studio.
        
        Note: LM Studio embedding support depends on the loaded model.
        """
        try:
            client = self._get_client()
            
            # Use the loaded model or specified embedding model
            embedding_model = self.config.extra_params.get(
                "embedding_model", 
                self.config.model_name
            )
            
            response = client.embeddings.create(
                model=embedding_model,
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"LM Studio embedding failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if LM Studio is available."""
        try:
            client = self._get_client()
            # Try to list models
            client.models.list()
            return True
        except Exception as e:
            logger.debug(f"LM Studio not available: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available LM Studio models."""
        try:
            client = self._get_client()
            models = client.models.list()
            
            return [m.id for m in models.data]
        except Exception as e:
            logger.error(f"Failed to list LM Studio models: {e}")
            return []
