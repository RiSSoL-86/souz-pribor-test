from typing import final

from django.apps import AppConfig


@final
class UsersConfig(AppConfig):
    """Configure the users application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
