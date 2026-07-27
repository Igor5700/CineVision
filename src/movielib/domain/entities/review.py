from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from movielib.domain.errors import DomainValidationError
from movielib.domain.value_objects.telegram_id import TelegramId


@dataclass(slots=True)
class Review:
    MAX_LENGTH = 2000

    telegram_id: TelegramId
    film_id: int
    text: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise DomainValidationError("Review text cannot be blank")
        if len(self.text) > self.MAX_LENGTH:
            raise DomainValidationError(f"Review text exceeds {self.MAX_LENGTH} characters")
