from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from apps.users.models import User
from apps.users.tests.factories import DEFAULT_PASSWORD, UserFactory

if TYPE_CHECKING:
    from django.test import Client


@pytest.mark.django_db
def test_signup_creates_user(client: Client) -> None:
    """Create a user without issuing tokens."""
    response = client.post(
        reverse("api:auth:signup"),
        data={"email": "new@example.com", "password": "secret-pass"},
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
    assert "accessToken" not in response.json()
    user = User.objects.get(email="new@example.com")
    assert user.check_password("secret-pass")


@pytest.mark.django_db
def test_signup_rejects_existing_email(client: Client) -> None:
    """Reject registration with an existing email."""
    UserFactory.create(email="existing@example.com")

    response = client.post(
        reverse("api:auth:signup"),
        data={"email": "existing@example.com", "password": "secret-pass"},
        content_type="application/json",
    )

    assert response.status_code == 409


@pytest.mark.django_db
def test_signin_returns_tokens(client: Client) -> None:
    """Issue tokens for valid credentials."""
    user = UserFactory.create()

    response = client.post(
        reverse("api:auth:signin"),
        data={"email": user.email, "password": DEFAULT_PASSWORD},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert response.json()["accessToken"]
    assert response.json()["refreshToken"]


@pytest.mark.django_db
def test_signin_rejects_invalid_credentials(client: Client) -> None:
    """Reject an invalid password."""
    user = UserFactory.create()

    response = client.post(
        reverse("api:auth:signin"),
        data={"email": user.email, "password": "wrong-password"},
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": [
            {
                "msg": "Not authenticated",
                "type": "security",
            },
        ],
    }


@pytest.mark.django_db
def test_refresh_returns_new_token_pair(client: Client) -> None:
    """Issue a new pair for a valid refresh token."""
    user = UserFactory.create()
    signin_response = client.post(
        reverse("api:auth:signin"),
        data={"email": user.email, "password": DEFAULT_PASSWORD},
        content_type="application/json",
    )
    old_tokens = signin_response.json()

    response = client.post(
        reverse("api:auth:refresh"),
        data={"refreshToken": old_tokens["refreshToken"]},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["accessToken"] != old_tokens["accessToken"]
    assert response.json()["refreshToken"] != old_tokens["refreshToken"]


@pytest.mark.django_db
def test_refresh_rejects_access_token(client: Client) -> None:
    """Reject an access token at the refresh endpoint."""
    user = UserFactory.create()
    signin_response = client.post(
        reverse("api:auth:signin"),
        data={"email": user.email, "password": DEFAULT_PASSWORD},
        content_type="application/json",
    )

    response = client.post(
        reverse("api:auth:refresh"),
        data={"refreshToken": signin_response.json()["accessToken"]},
        content_type="application/json",
    )

    assert response.status_code == 401
