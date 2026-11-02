from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class BaseRepository[ModelT: models.Model, PrimaryKeyT]:
    """Basic asynchronous CRUD operations for a Django model."""

    model: type[ModelT]

    async def get(self, primary_key: PrimaryKeyT) -> ModelT | None:
        """Return a model instance by its primary key or None."""
        try:
            return await self.model.objects.aget(  # type: ignore[no-any-return, attr-defined]
                pk=primary_key,
            )
        except ObjectDoesNotExist:
            return None

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModelT]:
        """Return a page of model instances."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")

        queryset = self.model.objects.order_by("pk")  # type: ignore[attr-defined]
        queryset = queryset[offset : offset + limit]
        return [instance async for instance in queryset]

    @staticmethod
    async def create(instance: ModelT) -> ModelT:
        """Persist a new model instance."""
        await instance.asave(force_insert=True)
        return instance

    async def update(
        self,
        primary_key: PrimaryKeyT,
        instance: ModelT,
    ) -> ModelT | None:
        """Replace a model instance identified by its primary key."""
        stored_instance = await self.get(primary_key)
        if stored_instance is None:
            return None

        instance.pk = stored_instance.pk
        await instance.asave(force_update=True)
        return instance

    async def delete(self, primary_key: PrimaryKeyT) -> None:
        """Delete a model instance identified by its primary key."""
        instance = await self.get(primary_key)
        if instance is not None:
            await instance.adelete()
