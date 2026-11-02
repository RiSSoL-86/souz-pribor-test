from http import HTTPStatus
from typing import final

from dmr import Controller, modify
from dmr.plugins.pydantic import PydanticSerializer
from dmr.security import AuthenticatedHttpRequest

from apps.users.models import User
from services.api.users.schemas import UserMeResponse
from services.api.users.services.me import UserMeService


@final
class UserMeController(Controller[PydanticSerializer]):
    """Return the authenticated user."""

    request: AuthenticatedHttpRequest[User]

    @modify(status_code=HTTPStatus.OK, tags=["Users"])
    async def get(self) -> UserMeResponse:
        """Return information about the authenticated user."""
        service = UserMeService()
        user = await service.execute(self.request.user)
        return UserMeResponse.model_validate(obj=user)
