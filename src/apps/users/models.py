from typing import ClassVar, final

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.users.managers import UserManager


@final
class User(AbstractUser):
    """Represent a user identified by email."""

    username = None  # type: ignore[assignment]

    email = models.EmailField(_("email"), unique=True)
    first_name = models.CharField(_("first name"), max_length=80)
    last_name = models.CharField(_("last name"), max_length=80)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects: ClassVar[UserManager] = UserManager()

    class Meta:
        """Define database constraints for users."""

        constraints = [
            models.UniqueConstraint(
                Lower("email"), name="unique_lowered_email"
            )
        ]
