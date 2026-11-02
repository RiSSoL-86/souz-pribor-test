from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, Mock

import httpx2
import openai
import pytest
from django.test import override_settings
from pydantic import BaseModel

from services.llm.exceptions import (
    LLMAccessDeniedError,
    LLMAuthenticationError,
    LLMBadResponseError,
    LLMError,
    LLMNotConfiguredError,
    LLMRateLimitError,
    LLMUnavailableError,
)
from services.llm.open_ai import OpenAIBackend
from services.llm.open_ai.client import OpenAIClient

REQUEST = httpx2.Request("POST", "https://api.openai.com/v1/responses")


class Answer(BaseModel):
    """Output schema used in the tests."""

    text: str


def _status_error(cls: type[openai.APIStatusError], code: int) -> Any:
    """Build an SDK error the way the SDK does for an HTTP status."""
    return cls(
        "error",
        response=httpx2.Response(code, request=REQUEST),
        body=None,
    )


def _client(parse: AsyncMock) -> OpenAIClient:
    """Wrap a fake SDK client whose responses.parse is ``parse``."""
    sdk = Mock()
    sdk.responses.parse = parse
    return OpenAIClient(client=sdk, model="test-model", temperature=0.3)


async def test_parse_returns_structured_output() -> None:
    """Return the parsed model and pass the call settings through."""
    parse = AsyncMock(
        return_value=SimpleNamespace(id="r1", output_parsed=Answer(text="ok")),
    )

    result = await _client(parse).parse(
        instructions="system",
        prompt="user",
        output_type=Answer,
    )

    assert result == Answer(text="ok")
    kwargs = parse.await_args.kwargs
    assert kwargs["model"] == "test-model"
    assert kwargs["instructions"] == "system"
    assert kwargs["input"] == "user"
    assert kwargs["text_format"] is Answer
    assert kwargs["temperature"] == 0.3


async def test_parse_without_output_is_bad_response() -> None:
    """Treat a refusal or an empty structured output as a bad response."""
    parse = AsyncMock(
        return_value=SimpleNamespace(id="r1", output_parsed=None)
    )

    with pytest.raises(LLMBadResponseError):
        await _client(parse).parse(
            instructions="system",
            prompt="user",
            output_type=Answer,
        )


@pytest.mark.parametrize(
    ("sdk_error", "expected"),
    [
        (
            _status_error(openai.AuthenticationError, 401),
            LLMAuthenticationError,
        ),
        (
            _status_error(openai.PermissionDeniedError, 403),
            LLMAccessDeniedError,
        ),
        (_status_error(openai.RateLimitError, 429), LLMRateLimitError),
        (_status_error(openai.InternalServerError, 500), LLMUnavailableError),
        (openai.APITimeoutError(request=REQUEST), LLMUnavailableError),
        (openai.APIConnectionError(request=REQUEST), LLMUnavailableError),
        (_status_error(openai.BadRequestError, 400), LLMBadResponseError),
    ],
)
async def test_parse_maps_sdk_errors(
    sdk_error: Exception,
    expected: type[LLMError],
) -> None:
    """Turn every SDK failure into one of the service's own errors."""
    parse = AsyncMock(side_effect=sdk_error)

    with pytest.raises(expected):
        await _client(parse).parse(
            instructions="system",
            prompt="user",
            output_type=Answer,
        )


@override_settings(OPENAI_API_KEY="")
def test_backend_requires_api_key() -> None:
    """Refuse to build a client without a key."""
    with pytest.raises(LLMNotConfiguredError):
        OpenAIBackend.get_client()


@override_settings(OPENAI_API_KEY="sk-test", OPENAI_MODEL="test-model")
def test_backend_builds_one_client() -> None:
    """Build the client once and reuse it."""
    OpenAIBackend._build_client.cache_clear()
    try:
        client = OpenAIBackend.get_client()

        assert isinstance(client, OpenAIClient)
        assert client.model == "test-model"
        assert OpenAIBackend.get_client() is client
    finally:
        OpenAIBackend._build_client.cache_clear()
