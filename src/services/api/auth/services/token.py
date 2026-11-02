import datetime as dt
import uuid
from typing import TYPE_CHECKING, Literal, final, override

from django.conf import settings
from dmr.security.jwt import JWToken

from services.api.common.services.base import BaseService

if TYPE_CHECKING:
    from apps.users.models import User


@final
class TokenService(BaseService):
    """Create JWT access and refresh tokens."""

    @override
    async def execute(self, user: User) -> tuple[str, str, str]:
        """Return the user email and a newly created JWT token pair."""
        now = dt.datetime.now(dt.UTC)
        access_token = self._create_token(
            user=user,
            expiration=(now + settings.JWT_ACCESS_TOKEN_LIFETIME),  # type: ignore[misc]
            token_type="access",
        )
        refresh_token = self._create_token(
            user=user,
            expiration=(now + settings.JWT_REFRESH_TOKEN_LIFETIME),  # type: ignore[misc]
            token_type="refresh",
        )
        return user.email, access_token, refresh_token

    @staticmethod
    def _create_token(
        user: User,
        expiration: dt.datetime,
        token_type: Literal["access", "refresh"],
    ) -> str:
        """Create an encoded JWT of the requested type."""
        return JWToken(
            sub=str(user.pk),
            exp=expiration,
            jti=uuid.uuid4().hex,
            extras={"type": token_type},
        ).encode(
            secret=settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,  # type: ignore[misc]
        )
