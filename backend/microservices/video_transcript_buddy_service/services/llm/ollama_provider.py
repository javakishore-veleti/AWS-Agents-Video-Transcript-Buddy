"""
Ollama Provider - Implementation for local Ollama models.

Ollama is a popular local LLM runner that supports models like:
- llama3.2, llama3.1
- mistral, mixtral
- codellama
- phi, gemma
- and many more

Default endpoint: http://localhost:11434
"""

import logging
import httpx
from typing import List, Optional, Dict, Any

from .provider_interface import LLMProvider, LLMProviderConfig, LLMResponse, ProviderType

logger = logging.getLogger(__name__)

# Default Ollama endpoint
DEFAULT_OLLAMA_URL = "http://localhost:11434"


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider implementation."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OLLAMA
    
    @property
    def base_url(self) -> str:
        """Get Ollama base URL."""
        return self.config.base_url or DEFAULT_OLLAMA_URL
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response using Ollama."""
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
        """Generate a chat response using Ollama."""
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.config.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.config.temperature,
                }
            }
            
            if max_tokens or self.config.max_tokens:
                payload["options"]["num_predict"] = max_tokens or self.config.max_tokens
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
            
            return LLMResponse(
                content=data.get("message", {}).get("content", ""),
                model=data.get("model", self.config.model_name),
                provider=self.provider_type,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                finish_reason=data.get("done_reason", "stop"),
                raw_response=data
            )
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding using Ollama."""
        try:
            url = f"{self.base_url}/api/embeddings"
            
            # Use nomic-embed-text or mxbai-embed-large for embeddings
            embedding_model = self.config.extra_params.get(
                "embedding_model", 
                "nomic-embed-text"
            )
            
            payload = {
                "model": embedding_model,
                "prompt": text
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
            
            return data.get("embedding", [])
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}")
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            url = f"{self.base_url}/api/tags"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            url = f"{self.base_url}/api/tags"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            models = [model.get("name", "") for model in data.get("models", [])]
            return sorted(models)
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model to Ollama.
        
        Args:
            model_name: Name of the model to pull (e.g., 'llama3.2')
            
        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/api/pull"
            
            payload = {"name": model_name, "stream": False}
            
            async with httpx.AsyncClient(timeout=None) as client:  # No timeout for downloads
                response = await client.post(url, json=payload)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull Ollama model {model_name}: {e}")
            return False
