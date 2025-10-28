from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def _validate_openai_api_key(v: str | None) -> str | None:
    """Validate that the OpenAI API key starts with 'sk-proj-'."""
    if v and not v.startswith("sk-proj-"):
        raise ValueError("OpenAI API key must start with 'sk-proj-'")
    return v


def _validate_exa_api_key(v: str | None) -> str | None:
    """Validate that the Exa API key is a valid UUID4."""
    if v:
        try:
            UUID(v, version=4)
        except ValueError:
            raise ValueError("Exa API key must be a valid UUID4") from None
    return v


def _validate_tavily_api_key(v: str | None) -> str | None:
    """Validate that the Tavily API key starts with 'tvly-'."""
    if v and not v.startswith("tvly-"):
        raise ValueError("Tavily API key must start with 'tvly-'")
    return v


def _validate_brave_api_key(v: str | None) -> str | None:
    """Validate that the Brave API key is a non-empty string."""
    if v and len(v.strip()) == 0:
        raise ValueError("Brave API key cannot be empty")
    return v


def _validate_google_api_key(v: str | None) -> str | None:
    """Validate that the Google API key starts with 'AIza'."""
    if v and not v.startswith("AIza"):
        raise ValueError("Google API key must start with 'AIza'")
    return v


def _validate_llm_provider(v: str | None) -> str | None:
    """Validate that the LLM provider is supported."""
    if v and v not in ["openai", "gemini"]:
        raise ValueError("LLM provider must be 'openai' or 'gemini'")
    return v


OpenAIAPIKey = Annotated[str | None, AfterValidator(_validate_openai_api_key)]
ExaAPIKey = Annotated[str | None, AfterValidator(_validate_exa_api_key)]
TavilyAPIKey = Annotated[str | None, AfterValidator(_validate_tavily_api_key)]
BraveAPIKey = Annotated[str | None, AfterValidator(_validate_brave_api_key)]
GoogleAPIKey = Annotated[str | None, AfterValidator(_validate_google_api_key)]
LLMProviderType = Annotated[str, AfterValidator(_validate_llm_provider)]


class Settings(BaseSettings):
    """Manages application settings and environment variables."""

    llm_provider: LLMProviderType = Field(default="openai", alias="LLM_PROVIDER")
    openai_api_key: OpenAIAPIKey = Field(default=None, alias="OPENAI_API_KEY")
    google_api_key: GoogleAPIKey = Field(default=None, alias="GOOGLE_API_KEY")
    exa_api_key: ExaAPIKey = Field(default=None, alias="EXA_API_KEY")
    tavily_api_key: TavilyAPIKey = Field(default=None, alias="TAVILY_API_KEY")
    brave_api_key: BraveAPIKey = Field(default=None, alias="BRAVE_API_KEY")
    redis_uri: RedisDsn = Field(default="redis://localhost:6379", alias="REDIS_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
