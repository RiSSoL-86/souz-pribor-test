import logging
from typing import TYPE_CHECKING, final, override

import openai

from services.llm.base import BaseLLMClient
from services.llm.exceptions import (
    LLMAccessDeniedError,
    LLMAuthenticationError,
    LLMBadResponseError,
    LLMRateLimitError,
    LLMUnavailableError,
)

if TYPE_CHECKING:
    from pydantic import BaseModel

logger = logging.getLogger(__name__)


@final
class OpenAIClient(BaseLLMClient):
    """Get structured answers from the OpenAI Responses API."""

    def __init__(
        self,
        client: openai.AsyncOpenAI,
        model: str,
        temperature: float,
    ) -> None:
        """Take the SDK client, already configured, and the call settings."""
        self.client = client
        self.model = model
        self.temperature = temperature

    @override
    async def parse[T: BaseModel](
        self,
        instructions: str,
        prompt: str,
        output_type: type[T],
    ) -> T:
        """Return the model answer validated against ``output_type``."""
        try:
            response = await self.client.responses.parse(
                model=self.model,
                instructions=instructions,
                input=prompt,
                text_format=output_type,
                temperature=self.temperature,
            )
        except openai.AuthenticationError as e:
            raise LLMAuthenticationError(str(e)) from e
        except openai.PermissionDeniedError as e:
            raise LLMAccessDeniedError(str(e)) from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError(str(e)) from e
        except (openai.APIConnectionError, openai.InternalServerError) as e:
            raise LLMUnavailableError(str(e)) from e
        except (openai.APIError, openai.OpenAIError) as e:
            raise LLMBadResponseError(str(e)) from e

        parsed = response.output_parsed
        if parsed is None:
            logger.warning(f"OpenAI returned no parsed output: {response.id}")
            raise LLMBadResponseError(
                "The model returned no structured output."
            )
        return parsed
