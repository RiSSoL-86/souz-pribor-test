from http import HTTPStatus
from typing import TYPE_CHECKING, override

from django.utils.encoding import force_str
from dmr import APIError
from dmr.errors import ErrorModel, ErrorType, format_error

if TYPE_CHECKING:
    from django.utils.functional import Promise


class BaseAPIError(APIError[ErrorModel]):
    """Build a user-facing API error in the standard DMR format."""

    message: str | Promise
    loc: str | list[str | int] | None = None
    status_code = HTTPStatus.BAD_REQUEST

    @override
    def __init__(self) -> None:
        """Initialize the configured API error."""

        super().__init__(
            format_error(
                force_str(self.message),
                loc=self.loc,
                error_type=ErrorType.user_msg,
            ),
            status_code=self.status_code,
        )
