import pytest
from django.contrib.auth import authenticate

from apps.users.models import User


@pytest.mark.django_db
class TestAuthenticationBackend:
    """Authenticate emails case-insensitively through the user manager."""

    def test_authenticate_with_exact_email(self):
        """Authenticate credentials containing the stored email casing."""
        # Arrange
        user = User.objects.create_user(
            email="user@example.com",
            password="secret",
        )

        # Act
        authenticated = authenticate(
            username="user@example.com",
            password="secret",
        )

        # Assert
        assert authenticated is not None
        assert authenticated.pk == user.pk

    def test_authenticate_is_case_insensitive(self):
        """Authenticate credentials containing different email casing."""
        # Arrange
        user = User.objects.create_user(
            email="user@example.com",
            password="secret",
        )

        # Act
        authenticated = authenticate(
            username="USER@EXAMPLE.COM",
            password="secret",
        )

        # Assert
        assert authenticated is not None
        assert authenticated.pk == user.pk

    def test_authenticate_with_wrong_password_fails(self):
        """Reject credentials containing an incorrect password."""
        # Arrange
        User.objects.create_user(
            email="user@example.com",
            password="secret",
        )

        # Act
        authenticated = authenticate(
            username="user@example.com",
            password="wrong",
        )

        # Assert
        assert authenticated is None

    def test_authenticate_unknown_email_fails(self):
        """Reject credentials containing an unknown email."""
        # Act
        authenticated = authenticate(
            username="ghost@example.com",
            password="secret",
        )

        # Assert
        assert authenticated is None
