from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from movielib.domain.errors import InvalidRatingScoreError
from movielib.domain.value_objects.telegram_id import TelegramId


@dataclass(slots=True)
class Rating:
    telegram_id: TelegramId
    film_id: int
    score: int
    rated_at: datetime

    def __post_init__(self) -> None:
        if not 1 <= self.score <= 10:
            raise InvalidRatingScoreError(self.score)
