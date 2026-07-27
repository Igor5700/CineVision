from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from movielib.domain.errors import DomainValidationError
from movielib.domain.value_objects.telegram_id import TelegramId


@dataclass(slots=True)
class Collection:
    id: int | None
    telegram_id: TelegramId
    name: str
    description: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainValidationError("Collection name cannot be blank")
