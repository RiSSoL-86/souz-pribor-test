import pytest
from django.test import override_settings

from services.llm import LLMBackend
from services.llm.exceptions import LLMNotConfiguredError
from services.llm.open_ai import OpenAIBackend
from services.llm.open_ai.client import OpenAIClient


@override_settings(LLM_PROVIDER="open_ai", OPENAI_API_KEY="sk-test")
def test_backend_gives_provider_client() -> None:
    """Return the client of the provider set in the settings."""
    OpenAIBackend._build_client.cache_clear()
    try:
        assert isinstance(LLMBackend.get_client(), OpenAIClient)
    finally:
        OpenAIBackend._build_client.cache_clear()


@override_settings(LLM_PROVIDER="unknown")
def test_backend_rejects_unknown_provider() -> None:
    """Refuse a provider that is not registered."""
    with pytest.raises(LLMNotConfiguredError):
        LLMBackend.get_client()
