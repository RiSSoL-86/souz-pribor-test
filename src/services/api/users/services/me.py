from typing import TYPE_CHECKING, final, override

from services.api.common.services.base import BaseService

if TYPE_CHECKING:
    from apps.users.models import User


@final
class UserMeService(BaseService):
    """Resolve the user exposed by the protected /me endpoint."""

    @override
    async def execute(self, user: User) -> User:
        """Return the user authenticated by the request token."""
        return user
