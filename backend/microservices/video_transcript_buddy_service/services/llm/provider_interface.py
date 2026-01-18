"""
LLM Provider Interface - Base class for all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    # Cloud Providers
    OPENAI = "openai"
    GEMINI = "gemini"           # Google Gemini - Coming Soon
    CLAUDE = "claude"           # Anthropic Claude - Coming Soon
    COPILOT = "copilot"         # Microsoft Copilot - Coming Soon
    
    # Local Providers
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    
    # Agentic / MCP
    N8N = "n8n"                 # n8n Agentic - Coming Soon
    MCP = "mcp"                 # MCP Server - Coming Soon
    
    # Custom
    CUSTOM = "custom"


class ProviderStatus(str, Enum):
    """Provider implementation status."""
    AVAILABLE = "available"
    COMING_SOON = "coming_soon"
    BETA = "beta"
    DEPRECATED = "deprecated"


# Provider metadata for UI display
PROVIDER_METADATA = {
    ProviderType.OPENAI: {
        "name": "OpenAI",
        "description": "GPT-4, GPT-3.5 Turbo",
        "status": ProviderStatus.AVAILABLE,
        "is_local": False,
        "requires_api_key": True,
        "icon": "openai",
        "default_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    },
    ProviderType.GEMINI: {
        "name": "Google Gemini",
        "description": "Gemini Pro, Gemini Ultra",
        "status": ProviderStatus.COMING_SOON,
        "is_local": False,
        "requires_api_key": True,
        "icon": "google",
        "default_models": ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]
    },
    ProviderType.CLAUDE: {
        "name": "Anthropic Claude",
        "description": "Claude 3 Opus, Sonnet, Haiku",
        "status": ProviderStatus.COMING_SOON,
        "is_local": False,
        "requires_api_key": True,
        "icon": "anthropic",
        "default_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    },
    ProviderType.COPILOT: {
        "name": "Microsoft Copilot",
        "description": "Azure OpenAI Service",
        "status": ProviderStatus.COMING_SOON,
        "is_local": False,
        "requires_api_key": True,
        "icon": "microsoft",
        "default_models": ["gpt-4", "gpt-35-turbo"]
    },
    ProviderType.OLLAMA: {
        "name": "Ollama",
        "description": "Local LLMs (Llama, Mistral, etc.)",
        "status": ProviderStatus.AVAILABLE,
        "is_local": True,
        "requires_api_key": False,
        "icon": "ollama",
        "default_models": ["llama3.2", "mistral", "codellama", "phi"]
    },
    ProviderType.LMSTUDIO: {
        "name": "LM Studio",
        "description": "Local model runner",
        "status": ProviderStatus.AVAILABLE,
        "is_local": True,
        "requires_api_key": False,
        "icon": "lmstudio",
        "default_models": []
    },
    ProviderType.N8N: {
        "name": "n8n Agentic",
        "description": "Workflow automation with AI",
        "status": ProviderStatus.COMING_SOON,
        "is_local": False,
        "requires_api_key": True,
        "icon": "n8n",
        "default_models": []
    },
    ProviderType.MCP: {
        "name": "MCP Server",
        "description": "Model Context Protocol",
        "status": ProviderStatus.COMING_SOON,
        "is_local": False,
        "requires_api_key": False,
        "icon": "mcp",
        "default_models": []
    },
}


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider."""
    provider_type: ProviderType
    model_name: str
    base_url: Optional[str] = None  # For local models or custom endpoints
    api_key: Optional[str] = None   # For OpenAI or authenticated endpoints
    temperature: float = 0.7
    max_tokens: int = 1000
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def openai(cls, model: str = "gpt-4", api_key: Optional[str] = None) -> "LLMProviderConfig":
        """Create OpenAI configuration."""
        return cls(
            provider_type=ProviderType.OPENAI,
            model_name=model,
            api_key=api_key
        )
    
    @classmethod
    def ollama(cls, model: str = "llama3.2", base_url: str = "http://localhost:11434") -> "LLMProviderConfig":
        """Create Ollama configuration."""
        return cls(
            provider_type=ProviderType.OLLAMA,
            model_name=model,
            base_url=base_url
        )
    
    @classmethod
    def lmstudio(cls, model: str = "local-model", base_url: str = "http://localhost:1234/v1") -> "LLMProviderConfig":
        """Create LM Studio configuration."""
        return cls(
            provider_type=ProviderType.LMSTUDIO,
            model_name=model,
            base_url=base_url
        )


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    model: str
    provider: ProviderType
    usage: Optional[Dict[str, int]] = None  # tokens used
    finish_reason: Optional[str] = None
    raw_response: Optional[Any] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self._client = None
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Standardized LLMResponse
        """
        pass
    
    @abstractmethod
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate a chat response from message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Standardized LLMResponse
        """
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the provider is available and configured.
        
        Returns:
            True if provider is ready to use
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        List available models for this provider.
        
        Returns:
            List of model names
        """
        pass
