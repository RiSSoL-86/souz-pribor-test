from typing import final

from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password

from apps.common.repository import BaseRepository
from apps.users.models import User


@final
class UserRepository(BaseRepository[User, int]):
    """Persistence operations for users."""

    model = User

    async def create_user(self, email: str, password: str) -> User:
        """Create a user with a normalized email and hashed password."""
        password_hash = await sync_to_async(
            func=make_password,
            thread_sensitive=False,
        )(password)
        user = User(
            email=User.objects.normalize_email(email),
            password=password_hash,
        )
        return await self.create(instance=user)
