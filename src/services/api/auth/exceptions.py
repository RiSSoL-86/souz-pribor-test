from http import HTTPStatus
from typing import final

from django.utils.translation import gettext_lazy as _

from services.api.common.exceptions import BaseAPIError


@final
class UserAlreadyExistsError(BaseAPIError):
    """Report an attempt to register an existing email."""

    message = _("An account with this email already exists.")
    loc = "email"
    status_code = HTTPStatus.CONFLICT
