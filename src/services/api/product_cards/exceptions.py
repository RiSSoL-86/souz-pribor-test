from http import HTTPStatus
from typing import final

from django.utils.translation import gettext_lazy as _

from services.api.common.exceptions import BaseAPIError
from services.llm.exceptions import (
    LLMAccessDeniedError,
    LLMAuthenticationError,
    LLMBadResponseError,
    LLMError,
    LLMNotConfiguredError,
    LLMRateLimitError,
    LLMUnavailableError,
)


@final
class NotEnoughProductDataError(BaseAPIError):
    """Report a product with neither specs nor a description."""

    message = _(
        "Недостаточно данных для карточки: заполните specs или description.",
    )
    loc = ["specs", "description"]
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY


@final
class LLMNotConfiguredAPIError(BaseAPIError):
    """Report that the service has no LLM API key."""

    message = _("Генерация недоступна: LLM не настроена, проверьте src/.env.")
    status_code = HTTPStatus.SERVICE_UNAVAILABLE


@final
class LLMAuthenticationAPIError(BaseAPIError):
    """Report that the LLM provider rejected the API key."""

    message = _("LLM-провайдер отклонил API-ключ: проверьте src/.env.")
    status_code = HTTPStatus.BAD_GATEWAY


@final
class LLMAccessDeniedAPIError(BaseAPIError):
    """Report that the LLM provider refused access from this region."""

    message = _(
        "LLM-провайдер отказал в доступе: регион не поддерживается "
        "или нет доступа к модели. Проверьте OPENAI_PROXY и OPENAI_MODEL.",
    )
    status_code = HTTPStatus.BAD_GATEWAY


@final
class LLMRateLimitAPIError(BaseAPIError):
    """Report a quota or rate limit hit on the LLM provider side."""

    message = _("Превышен лимит запросов к LLM. Повторите позже.")
    status_code = HTTPStatus.SERVICE_UNAVAILABLE


@final
class LLMUnavailableAPIError(BaseAPIError):
    """Report that the LLM provider could not be reached in time."""

    message = _("LLM недоступна или не ответила вовремя. Повторите позже.")
    status_code = HTTPStatus.SERVICE_UNAVAILABLE


@final
class LLMBadResponseAPIError(BaseAPIError):
    """Report an LLM answer that could not be turned into a card."""

    message = _("LLM вернула некорректный ответ. Повторите запрос.")
    status_code = HTTPStatus.BAD_GATEWAY


LLM_API_ERRORS: dict[type[LLMError], type[BaseAPIError]] = {
    LLMNotConfiguredError: LLMNotConfiguredAPIError,
    LLMAuthenticationError: LLMAuthenticationAPIError,
    LLMAccessDeniedError: LLMAccessDeniedAPIError,
    LLMRateLimitError: LLMRateLimitAPIError,
    LLMUnavailableError: LLMUnavailableAPIError,
    LLMBadResponseError: LLMBadResponseAPIError,
}


def to_api_error(error: LLMError) -> BaseAPIError:
    """Turn a provider error into the error the client is shown."""
    api_error = LLM_API_ERRORS.get(type(error), LLMBadResponseAPIError)
    return api_error()
