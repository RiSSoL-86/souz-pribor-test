from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from apps.users.tests.factories import DEFAULT_PASSWORD, UserFactory

if TYPE_CHECKING:
    from django.test import Client


@pytest.mark.django_db
def test_me_returns_authenticated_user(client: Client) -> None:
    """Return the user identified by the access token."""
    user = UserFactory.create()
    signin_response = client.post(
        reverse("api:auth:signin"),
        data={"email": user.email, "password": DEFAULT_PASSWORD},
        content_type="application/json",
    )

    response = client.get(
        reverse("api:users:me"),
        headers={
            "Authorization": (
                f"Bearer {signin_response.json()['accessToken']}"
            ),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": user.pk,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "isActive": True,
    }


@pytest.mark.django_db
def test_me_requires_access_token(client: Client) -> None:
    """Reject an unauthenticated request."""
    response = client.get(reverse("api:users:me"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_me_rejects_refresh_token(client: Client) -> None:
    """Reject a refresh token when an access token is required."""
    user = UserFactory.create()
    signin_response = client.post(
        reverse("api:auth:signin"),
        data={"email": user.email, "password": DEFAULT_PASSWORD},
        content_type="application/json",
    )

    response = client.get(
        reverse("api:users:me"),
        headers={
            "Authorization": (
                f"Bearer {signin_response.json()['refreshToken']}"
            ),
        },
    )

    assert response.status_code == 401
