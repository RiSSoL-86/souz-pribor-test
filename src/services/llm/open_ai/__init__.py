from functools import lru_cache
from typing import TYPE_CHECKING, final

import openai
from django.conf import settings

from services.llm.exceptions import LLMNotConfiguredError
from services.llm.open_ai.client import OpenAIClient

if TYPE_CHECKING:
    from services.llm.base import BaseLLMClient

__all__ = ["OpenAIBackend"]


@final
class OpenAIBackend:
    """Give out the OpenAI pieces a service is to work through."""

    @classmethod
    def get_client(cls) -> BaseLLMClient:
        """Return the client the product cards are written with."""
        if not settings.OPENAI_API_KEY:  # type: ignore[misc]
            raise LLMNotConfiguredError("OPENAI_API_KEY is not set.")
        return cls._build_client()

    @classmethod
    @lru_cache(maxsize=1)
    def _build_client(cls) -> BaseLLMClient:
        """Build the client once: the SDK keeps a connection pool."""
        sdk_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,  # type: ignore[misc]
            timeout=settings.OPENAI_TIMEOUT,  # type: ignore[misc]
            max_retries=settings.OPENAI_MAX_RETRIES,  # type: ignore[misc]
            http_client=openai.DefaultAsyncHttpxClient(
                proxy=settings.OPENAI_PROXY or None,  # type: ignore[misc]
            ),
        )
        return OpenAIClient(
            client=sdk_client,
            model=settings.OPENAI_MODEL,  # type: ignore[misc]
            temperature=settings.OPENAI_TEMPERATURE,  # type: ignore[misc]
        )
