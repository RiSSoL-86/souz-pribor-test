from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseLLMClient(ABC):
    """Ask a language model for an answer shaped as a given schema."""

    @abstractmethod
    async def parse[T: BaseModel](
        self,
        instructions: str,
        prompt: str,
        output_type: type[T],
    ) -> T:
        """Return the model answer validated against ``output_type``."""
        raise NotImplementedError
