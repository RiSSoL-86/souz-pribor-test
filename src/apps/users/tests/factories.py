import factory
from factory.django import DjangoModelFactory

from apps.users.models import User

# Shared raw password for factory-built users; authenticate tests with it.
DEFAULT_PASSWORD = "password"


class UserFactory(DjangoModelFactory[User]):
    """Build users with valid defaults for tests."""

    class Meta:
        """Configure the generated Django model."""

        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = "John"
    last_name = "Doe"
    # Stores an already-hashed password (no extra post-generation save).
    password = factory.django.Password(DEFAULT_PASSWORD)
