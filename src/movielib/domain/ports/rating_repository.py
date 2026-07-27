from __future__ import annotations

from typing import Protocol

from movielib.domain.entities.rating import Rating
from movielib.domain.value_objects.telegram_id import TelegramId


class RatingRepository(Protocol):
    async def rate(self, rating: Rating) -> None: ...

    async def get_my_rating(self, telegram_id: TelegramId, film_id: int) -> Rating | None: ...

    async def list_my_ratings(self, telegram_id: TelegramId) -> list[Rating]: ...

    async def average_for_film(self, film_id: int) -> float | None: ...
