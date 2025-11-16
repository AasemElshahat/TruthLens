"""Unified LLM model instances and factory functions.

Provides access to configured language model instances for all modules.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import Field

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
        model_name: str = "gemini-2.5-flash-lite",  # Latest and most cost-effective model
        temperature: float = 0.0,
        completions: int = 1,
    ) -> BaseChatModel:
        """Get Google LLM instance with specified configuration."""
        # Use higher temp when doing multiple completions for diversity
        if completions > 1 and temperature == 0.0:
            temperature = 0.2

        if not settings.google_api_key:
            raise ValueError("Google API key not found in environment variables")

        from langchain_google_genai import ChatGoogleGenerativeAI
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=settings.google_api_key,
            temperature=temperature,
        )


logger = logging.getLogger(__name__)

class DeepSeekChatWrapper(BaseChatModel):
    """Wrapper for DeepSeek to handle structured output manually."""

    actual_llm: Any = Field(default=None, exclude=True)  # Use Field to properly define the attribute

    def __init__(self, actual_llm, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'actual_llm', actual_llm)

    @property
    def _llm_type(self) -> str:
        return "deepseek-chat-wrapper"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return self.actual_llm._identifying_params

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager=None,
        **kwargs
    ):
        """Generate response from DeepSeek API."""
        return self.actual_llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    def bind(self, **kwargs):
        """Bind parameters to the underlying LLM."""
        return self.actual_llm.bind(**kwargs)

    def with_structured_output(self, schema, **kwargs):
        """
        Override with_structured_output to use JSON mode instead of schema mode for DeepSeek.
        This bypasses the incompatible response_format schema for DeepSeek.
        """
        # Create a callable class that has the same interface as an LLM with structured output
        class StructuredOutputWrapper:
                def __init__(self, actual_llm: BaseChatModel, schema):
                    self.actual_llm = actual_llm
                    self.schema = schema

                def _build_example_json(self) -> str:
                    fields = getattr(self.schema, "model_fields", None)
                    if not fields:
                        return "{}"

                    fragments = []
                    for field_name, field_def in fields.items():
                        annotation = getattr(field_def, "annotation", None)
                        type_name = getattr(annotation, "__name__", str(annotation)) if annotation else "value"
                        fragments.append(f'"{field_name}": <{type_name}>')

                    return "{" + ", ".join(fragments) + "}"

                def _format_request_with_json_instruction(
                    self, messages: List[BaseMessage]
                ) -> List[BaseMessage]:
                    """Add JSON response instructions to the final message."""
                    if not messages:
                        return messages

                    enhanced_messages = list(messages)
                    example_json = self._build_example_json()
                    last_msg = enhanced_messages[-1]
                    instruction = (
                        "Please respond ONLY with valid JSON that matches this shape: "
                        f"{example_json}. Do not include explanations or prose."
                    )
                    new_content = f"{last_msg.content}\n\n{instruction}" if last_msg.content else instruction

                    try:
                        enhanced_messages[-1] = last_msg.model_copy(update={"content": new_content})
                    except Exception:
                        enhanced_messages[-1] = last_msg.__class__(content=new_content)

                    return enhanced_messages

                def _coerce_text_content(self, content: Any) -> str:
                    if isinstance(content, str):
                        return content

                    if isinstance(content, list):
                        fragments = []
                        for chunk in content:
                            if isinstance(chunk, dict):
                                if chunk.get("type") == "text":
                                    fragments.append(chunk.get("text", ""))
                            elif hasattr(chunk, "dict"):
                                data = chunk.dict()
                                if data.get("type") == "text":
                                    fragments.append(data.get("text", ""))
                            elif isinstance(chunk, str):
                                fragments.append(chunk)
                        return "".join(fragments)

                    return str(content)

                def _extract_json_segment(self, text: str) -> Optional[str]:
                    if not text:
                        return None

                    text = text.strip()

                    # Prefer fenced code blocks if present
                    fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
                    if fence_match:
                        return fence_match.group(1).strip()

                    start = text.find("{")
                    if start == -1:
                        return None

                    depth = 0
                    for idx in range(start, len(text)):
                        char = text[idx]
                        if char == "{":
                            depth += 1
                        elif char == "}":
                            depth -= 1
                            if depth == 0:
                                return text[start : idx + 1]
                    return None

                def _parse_response(self, content: Any):
                    text = self._coerce_text_content(content)
                    json_payload = self._extract_json_segment(text)

                    if not json_payload:
                        logger.debug("DeepSeek response missing JSON payload: %s", text[:200])
                        return self.schema()

                    try:
                        parsed_data = json.loads(json_payload)
                        return self.schema(**parsed_data) if parsed_data else self.schema()
                    except (json.JSONDecodeError, TypeError, ValueError) as exc:
                        logger.warning("Failed to parse DeepSeek JSON response: %s", exc)
                        return self.schema()

                def invoke(self, messages: List[BaseMessage], **llm_kwargs):
                    formatted_messages = self._format_request_with_json_instruction(messages)
                    response = self.actual_llm.invoke(formatted_messages, **llm_kwargs)
                    return self._parse_response(response.content)

                async def ainvoke(self, messages: List[BaseMessage], **llm_kwargs):
                    formatted_messages = self._format_request_with_json_instruction(messages)
                    response = await self.actual_llm.ainvoke(formatted_messages, **llm_kwargs)
                    return self._parse_response(response.content)

        # Return an instance of the wrapper class that has the proper interface
        return StructuredOutputWrapper(self.actual_llm, schema)

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

        # Create the actual LLM with JSON object response format
        actual_llm = ChatOpenAI(
            model=model_name,
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com",
            temperature=temperature,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        # Wrap it to handle structured output differently
        return DeepSeekChatWrapper(actual_llm)


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
            model_name = "gemini-2.5-flash-lite"
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
