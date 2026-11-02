from typing import TYPE_CHECKING, final

from django.conf import settings

from services.llm.exceptions import LLMNotConfiguredError
from services.llm.open_ai import OpenAIBackend

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.llm.base import BaseLLMClient

__all__ = ["LLMBackend"]

PROVIDERS: dict[str, Callable[[], BaseLLMClient]] = {
    "open_ai": OpenAIBackend.get_client,
}


@final
class LLMBackend:
    """Give out the client of the provider chosen in the settings."""

    @classmethod
    def get_client(cls) -> BaseLLMClient:
        """Return the client of ``settings.LLM_PROVIDER``."""
        provider = settings.LLM_PROVIDER  # type: ignore[misc]
        get_client = PROVIDERS.get(provider)
        if get_client is None:
            raise LLMNotConfiguredError(f"Unknown LLM provider: {provider!r}.")
        return get_client()
