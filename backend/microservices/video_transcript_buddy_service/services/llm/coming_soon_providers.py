"""
Coming Soon Provider Facades - Placeholder implementations for upcoming LLM providers.

These facades define the interface and will be implemented when the features are ready.
"""

from typing import List, Optional, Dict, Any
from .provider_interface import LLMProvider, LLMProviderConfig, LLMResponse, ProviderType, ProviderStatus


class ComingSoonProvider(LLMProvider):
    """
    Base class for providers that are not yet implemented.
    Raises NotImplementedError with helpful message.
    """
    
    provider_name: str = "Coming Soon"
    provider_type: ProviderType = ProviderType.CUSTOM
    status: ProviderStatus = ProviderStatus.COMING_SOON
    eta: str = "TBD"
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Not implemented - coming soon."""
        raise NotImplementedError(
            f"{self.provider_name} integration is coming soon (ETA: {self.eta}). "
            f"Please use OpenAI, Ollama, or LM Studio in the meantime."
        )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ):
        """Not implemented - coming soon."""
        raise NotImplementedError(
            f"{self.provider_name} streaming is coming soon (ETA: {self.eta})."
        )
    
    async def list_models(self) -> List[str]:
        """Return placeholder models."""
        return []
    
    async def health_check(self) -> bool:
        """Always returns False for coming soon providers."""
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Return provider status."""
        return {
            "provider": self.provider_name,
            "type": self.provider_type.value,
            "status": self.status.value,
            "available": False,
            "eta": self.eta,
            "message": f"Coming soon - ETA {self.eta}"
        }


class GeminiProvider(ComingSoonProvider):
    """
    Google Gemini Provider - Coming Soon
    
    Will support:
    - gemini-pro
    - gemini-pro-vision
    - gemini-ultra
    
    Features planned:
    - Multi-modal support (text + images)
    - Long context windows
    - Function calling
    """
    
    provider_name = "Google Gemini"
    provider_type = ProviderType.GEMINI
    eta = "Q2 2026"
    
    # Future implementation notes:
    # - Use google.generativeai SDK
    # - Requires GOOGLE_API_KEY
    # - Support for vision models


class ClaudeProvider(ComingSoonProvider):
    """
    Anthropic Claude Provider - Coming Soon
    
    Will support:
    - claude-3-opus
    - claude-3-sonnet
    - claude-3-haiku
    
    Features planned:
    - 200K context window
    - Constitutional AI safety
    - Tool use / function calling
    """
    
    provider_name = "Anthropic Claude"
    provider_type = ProviderType.CLAUDE
    eta = "Q2 2026"
    
    # Future implementation notes:
    # - Use anthropic SDK
    # - Requires ANTHROPIC_API_KEY
    # - Support for tool_use


class CopilotProvider(ComingSoonProvider):
    """
    Microsoft Copilot Provider - Coming Soon
    
    Will support:
    - Azure OpenAI Service integration
    - Microsoft 365 Copilot APIs
    
    Features planned:
    - Enterprise SSO
    - Azure AD integration
    - Compliance features
    """
    
    provider_name = "Microsoft Copilot"
    provider_type = ProviderType.COPILOT
    eta = "Q3 2026"
    
    # Future implementation notes:
    # - Use azure-openai SDK
    # - Requires AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT
    # - Support for deployment names


class N8NAgenticProvider(ComingSoonProvider):
    """
    n8n Agentic Provider - Coming Soon
    
    Will support:
    - Workflow automation with AI
    - Custom tool chains
    - Multi-step agentic workflows
    
    Features planned:
    - Connect to n8n cloud or self-hosted
    - Trigger workflows from chat
    - Use workflow results in responses
    """
    
    provider_name = "n8n Agentic"
    provider_type = ProviderType.N8N
    eta = "Q3 2026"
    
    # Future implementation notes:
    # - Use n8n API
    # - Requires N8N_API_KEY and N8N_URL
    # - Support for webhook triggers


class MCPServerProvider(ComingSoonProvider):
    """
    MCP Server Provider - Coming Soon
    
    Will support:
    - Model Context Protocol (MCP) servers
    - External tool and resource access
    - Custom data sources
    
    Features planned:
    - Connect to any MCP-compatible server
    - Dynamic tool discovery
    - Resource access (files, databases, APIs)
    """
    
    provider_name = "MCP Server"
    provider_type = ProviderType.MCP
    eta = "Q2 2026"
    
    # Future implementation notes:
    # - Use MCP SDK
    # - Support stdio, HTTP, WebSocket transports
    # - Tool and resource management


# Registry of coming soon providers
COMING_SOON_PROVIDERS = {
    ProviderType.GEMINI: GeminiProvider,
    ProviderType.CLAUDE: ClaudeProvider,
    ProviderType.COPILOT: CopilotProvider,
    ProviderType.N8N: N8NAgenticProvider,
    ProviderType.MCP: MCPServerProvider,
}


def get_coming_soon_status() -> List[Dict[str, Any]]:
    """Get status of all coming soon providers."""
    return [
        {
            "provider": provider_type.value,
            "name": provider_class.provider_name,
            "eta": provider_class.eta,
            "status": "coming_soon"
        }
        for provider_type, provider_class in COMING_SOON_PROVIDERS.items()
    ]
