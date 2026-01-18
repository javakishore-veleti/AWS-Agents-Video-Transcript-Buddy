"""
LLM Provider Module - Abstraction layer for multiple LLM providers.

Supports:
- OpenAI API (Available)
- Ollama (Available - local)
- LM Studio (Available - local)

Coming Soon:
- Google Gemini
- Anthropic Claude
- Microsoft Copilot
- n8n Agentic
- MCP Server integration
"""

from .provider_interface import (
    LLMProvider, 
    LLMProviderConfig, 
    LLMResponse, 
    ProviderType,
    ProviderStatus,
    PROVIDER_METADATA
)
from .provider_factory import LLMProviderFactory, get_llm_provider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .lmstudio_provider import LMStudioProvider
from .coming_soon_providers import (
    ComingSoonProvider,
    GeminiProvider,
    ClaudeProvider,
    CopilotProvider,
    N8NAgenticProvider,
    MCPServerProvider,
    COMING_SOON_PROVIDERS,
    get_coming_soon_status
)

__all__ = [
    # Core
    'LLMProvider',
    'LLMProviderConfig',
    'LLMResponse',
    'ProviderType',
    'ProviderStatus',
    'PROVIDER_METADATA',
    
    # Factory
    'LLMProviderFactory',
    'get_llm_provider',
    
    # Available Providers
    'OpenAIProvider',
    'OllamaProvider',
    'LMStudioProvider',
    
    # Coming Soon
    'ComingSoonProvider',
    'GeminiProvider',
    'ClaudeProvider',
    'CopilotProvider',
    'N8NAgenticProvider',
    'MCPServerProvider',
    'COMING_SOON_PROVIDERS',
    'get_coming_soon_status',
]
