"""
OpenAI Provider - Implementation for OpenAI API.
"""

import logging
from typing import List, Optional, Dict, Any

from .provider_interface import LLMProvider, LLMProviderConfig, LLMResponse, ProviderType

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    def _get_client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                
                api_key = self.config.api_key
                if not api_key:
                    from config.settings import settings
                    api_key = settings.OPENAI_API_KEY
                
                if not api_key:
                    raise ValueError("OpenAI API key not configured")
                
                self._client = OpenAI(api_key=api_key)
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
        """Generate a response using OpenAI."""
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
        """Generate a chat response using OpenAI."""
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
                model=response.model,
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
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding using OpenAI."""
        try:
            client = self._get_client()
            
            from config.settings import settings
            embedding_model = self.config.extra_params.get(
                "embedding_model", 
                settings.OPENAI_EMBEDDING_MODEL
            )
            
            response = client.embeddings.create(
                model=embedding_model,
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            client = self._get_client()
            # Quick test - list models
            client.models.list()
            return True
        except Exception as e:
            logger.warning(f"OpenAI not available: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available OpenAI models."""
        try:
            client = self._get_client()
            models = client.models.list()
            
            # Filter for chat models
            chat_models = [
                m.id for m in models.data 
                if 'gpt' in m.id.lower() and 'instruct' not in m.id.lower()
            ]
            
            return sorted(chat_models)
        except Exception as e:
            logger.error(f"Failed to list OpenAI models: {e}")
            # Return common models as fallback
            return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
