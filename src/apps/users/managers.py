from typing import TYPE_CHECKING, Any, final, override

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager

if TYPE_CHECKING:
    from apps.users.models import User


@final
class UserManager(DjangoUserManager["User"]):
    """Manage users identified by email."""

    @override
    def create_user(  # type: ignore[override]
        self,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """Create a regular user."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user_with_email(email, password, **extra_fields)

    @override
    def create_superuser(  # type: ignore[override]
        self,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """Create a superuser."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user_with_email(email, password, **extra_fields)

    def _create_user_with_email(
        self,
        email: str | None,
        password: str | None,
        **extra_fields: Any,
    ) -> User:
        """Create and persist a user with a hashed password."""

        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    @override
    def get_by_natural_key(self, username: str | None) -> User:
        """Return a user by case-insensitive email."""

        ci_field = f"{self.model.USERNAME_FIELD}__iexact"
        return self.get(**{ci_field: username})
