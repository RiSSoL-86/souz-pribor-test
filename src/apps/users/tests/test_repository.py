import pytest

from apps.users.models import User
from apps.users.repository import UserRepository


@pytest.mark.django_db(transaction=True)
async def test_repository_get_returns_user() -> None:
    """Return a persisted user by primary key."""
    repository = UserRepository()
    user = await repository.create_user("stored@example.com", "password")

    result = await repository.get(user.pk)

    assert result == user


@pytest.mark.django_db(transaction=True)
async def test_repository_get_returns_none_for_unknown_key() -> None:
    """Return None when a primary key does not identify a user."""
    result = await UserRepository().get(1)

    assert result is None


@pytest.mark.django_db(transaction=True)
async def test_repository_lists_requested_page() -> None:
    """Apply limit and offset while listing persisted users."""
    repository = UserRepository()
    await repository.create_user("first@example.com", "password")
    await repository.create_user("second@example.com", "password")
    await repository.create_user("third@example.com", "password")
    all_users = await repository.list()

    page = await repository.list(limit=1, offset=1)

    assert page == all_users[1:2]


@pytest.mark.django_db(transaction=True)
async def test_repository_rejects_invalid_page() -> None:
    """Reject non-positive limits and negative offsets."""
    repository = UserRepository()

    with pytest.raises(ValueError, match="limit"):
        await repository.list(limit=0)
    with pytest.raises(ValueError, match="offset"):
        await repository.list(offset=-1)


@pytest.mark.django_db(transaction=True)
async def test_repository_updates_existing_user() -> None:
    """Replace an existing user while retaining its primary key."""
    repository = UserRepository()
    stored = await repository.create_user("stored@example.com", "password")
    replacement = User(
        email="updated@example.com",
        password=stored.password,
    )

    result = await repository.update(stored.pk, replacement)

    assert result is replacement
    assert result.pk == stored.pk
    assert (await repository.get(stored.pk)).email == "updated@example.com"  # type: ignore[union-attr]


@pytest.mark.django_db(transaction=True)
async def test_repository_update_returns_none_for_unknown_key() -> None:
    """Return None instead of inserting an unknown replacement model."""
    replacement = User(email="unknown@example.com", password="password")

    result = await UserRepository().update(1, replacement)

    assert result is None
    assert replacement.pk is None


@pytest.mark.django_db(transaction=True)
async def test_repository_deletes_existing_user() -> None:
    """Delete the user identified by a primary key."""
    repository = UserRepository()
    user = await repository.create_user("delete@example.com", "password")

    await repository.delete(user.pk)

    assert await repository.get(user.pk) is None


@pytest.mark.django_db(transaction=True)
async def test_repository_ignores_unknown_delete_key() -> None:
    """Complete deletion successfully when the user does not exist."""
    await UserRepository().delete(1)
