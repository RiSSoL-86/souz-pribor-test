import uuid

from django.db import models

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel


def test_uuid_model_is_abstract() -> None:
    """Provide an abstract model with an immutable UUID primary key."""
    assert UUIDAbstractModel._meta.abstract is True

    identifier = UUIDAbstractModel._meta.get_field("id")
    assert isinstance(identifier, models.UUIDField)
    assert identifier.primary_key is True
    assert identifier.editable is False
    assert isinstance(identifier.get_default(), uuid.UUID)


def test_timestamp_model_is_abstract() -> None:
    """Provide an abstract model with managed creation and update times."""
    assert TimestampedAbstractModel._meta.abstract is True

    created = TimestampedAbstractModel._meta.get_field("created_timestamp")
    updated = TimestampedAbstractModel._meta.get_field("updated_timestamp")

    assert isinstance(created, models.DateTimeField)
    assert created.auto_now_add is True
    assert created.editable is False
    assert isinstance(updated, models.DateTimeField)
    assert updated.auto_now is True
    assert updated.editable is False
