"""Unified LLM model instances and factory functions.

Provides access to configured language model instances for all modules.
"""

from abc import ABC, abstractmethod
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from utils.settings import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def invoke(
        self,
        model_name: str = None,
        temperature: float = 0.0,
        completions: int = 1,
    ) -> BaseChatModel:
        """Get LLM instance with specified configuration.
        
        Args:
            model_name: The model to use (provider-specific format)
            temperature: Temperature for generation
            completions: How many completions we need (affects temperature for diversity)
            
        Returns:
            Configured LLM instance
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""
    
    def invoke(
        self,
        model_name: str = "openai:gpt-4o-mini",
        temperature: float = 0.0,
        completions: int = 1,
    ) -> BaseChatModel:
        """Get OpenAI LLM instance with specified configuration."""
        # Use higher temp when doing multiple completions for diversity
        if completions > 1 and temperature == 0.0:
            temperature = 0.2

        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")

        return init_chat_model(
            model=model_name,
            api_key=settings.openai_api_key,
            temperature=temperature if model_name.startswith("openai:gpt") else None,
        )


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""
    
    def invoke(
        self,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.0,
        completions: int = 1,
    ) -> BaseChatModel:
        """Get Google LLM instance with specified configuration."""
        # Use higher temp when doing multiple completions for diversity
        if completions > 1 and temperature == 0.0:
            temperature = 0.2

        if not settings.google_api_key:
            raise ValueError("Google API key not found in environment variables")

        return init_chat_model(
            model=model_name,
            model_provider="google-genai",
            api_key=settings.google_api_key,
            temperature=temperature,
        )


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM provider implementation."""
    
    def invoke(
        self,
        model_name: str = "deepseek-chat",
        temperature: float = 0.0,
        completions: int = 1,
    ) -> BaseChatModel:
        """Get DeepSeek LLM instance with specified configuration."""
        # Use higher temp when doing multiple completions for diversity
        if completions > 1 and temperature == 0.0:
            temperature = 0.2

        if not settings.deepseek_api_key:
            raise ValueError("DeepSeek API key not found in environment variables")

        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            model=model_name,
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com",
            temperature=temperature,
        )


# Provider cache for singleton pattern - avoids recreating instances
_PROVIDER_CACHE = {}


def get_llm(
    model_name: str = None,
    temperature: float = 0.0,
    completions: int = 1,
    provider: str = None,
) -> BaseChatModel:
    """Get LLM with specified configuration.

    Args:
        model_name: The model to use (provider-specific format). If None, uses provider-appropriate default.
        temperature: Temperature for generation
        completions: How many completions we need (affects temperature for diversity)
        provider: LLM provider to use ("openai", "gemini", "deepseek"). If None, uses configured default.

    Returns:
        Configured LLM instance
    """
    # Use configured default provider if none specified
    if provider is None:
        provider = settings.llm_provider
    
    # Use provider-appropriate default model name if none specified
    if model_name is None:
        if provider == "openai":
            model_name = "openai:gpt-4o-mini"
        elif provider == "gemini":
            model_name = "gemini-1.5-flash"
        elif provider == "deepseek":
            model_name = "deepseek-chat"
    
    # Use singleton pattern for provider instances to avoid recreation overhead
    if provider not in _PROVIDER_CACHE:
        if provider == "openai":
            _PROVIDER_CACHE[provider] = OpenAIProvider()
        elif provider == "gemini":
            _PROVIDER_CACHE[provider] = GeminiProvider()
        elif provider == "deepseek":
            _PROVIDER_CACHE[provider] = DeepSeekProvider()
        else:
            supported_providers = ["openai", "gemini", "deepseek"]
            raise ValueError(f"Unknown provider: {provider}. Supported providers: {supported_providers}")
    
    provider_instance = _PROVIDER_CACHE[provider]
    return provider_instance.invoke(
        model_name=model_name,
        temperature=temperature,
        completions=completions,
    )


def get_default_llm() -> BaseChatModel:
    """Get default LLM instance using configured provider and default model."""
    return get_llm()
