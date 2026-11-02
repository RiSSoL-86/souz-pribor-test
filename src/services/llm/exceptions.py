class LLMError(Exception):
    """Base error of a language model call."""


class LLMNotConfiguredError(LLMError):
    """The provider has no API key to work with."""


class LLMAuthenticationError(LLMError):
    """The provider rejected the API key."""


class LLMAccessDeniedError(LLMError):
    """The provider refused access from this region or to this model."""


class LLMRateLimitError(LLMError):
    """The provider refused the call because of a quota or rate limit."""


class LLMUnavailableError(LLMError):
    """The provider could not be reached or timed out."""


class LLMBadResponseError(LLMError):
    """The provider answered with something that is not a usable result."""
