from typing import TYPE_CHECKING, final, override

from django.db import IntegrityError

from apps.users.repository import UserRepository
from services.api.auth.exceptions import UserAlreadyExistsError
from services.api.common.services.base import BaseService

if TYPE_CHECKING:
    from apps.users.models import User
    from services.api.auth.schemas import SignUpRequest


@final
class SignUpService(BaseService):
    """Register a new user account."""

    user_repository = UserRepository()

    @override
    async def execute(self, payload: SignUpRequest) -> User:
        """Create a user from email and password."""
        try:
            user = await self.user_repository.create_user(
                email=str(payload.email),
                password=payload.password,
            )
        except IntegrityError as error:
            raise UserAlreadyExistsError from error

        return user
