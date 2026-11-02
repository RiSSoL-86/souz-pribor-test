from typing import TYPE_CHECKING, final, override

from dmr.exceptions import NotAuthenticatedError
from dmr.security.jwt import JWTAsyncAuth

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from dmr.security.jwt import JWToken


@final
class AccessTokenAuth(JWTAsyncAuth):
    """Authenticate protected endpoints with access tokens only."""

    @override
    async def check_auth(
        self,
        user: AbstractBaseUser,
        token: JWToken,
    ) -> None:
        """Reject inactive users and tokens not marked as access tokens."""
        await super().check_auth(user, token)
        if token.extras.get("type") != "access":
            raise NotAuthenticatedError
