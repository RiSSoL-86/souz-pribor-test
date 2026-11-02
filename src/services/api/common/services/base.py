from abc import ABC, abstractmethod
from typing import Any


class BaseService(ABC):
    """Base class for all application services."""

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Run the business operation."""
        raise NotImplementedError
