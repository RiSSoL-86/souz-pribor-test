from typing import final

from pydantic import Field

from services.api.common.schemas import CamelCaseModel


@final
class UserMeResponse(CamelCaseModel):
    """Current authenticated user."""

    id: int
    email: str
    first_name: str = Field(max_length=80)
    last_name: str = Field(max_length=80)
    is_active: bool
