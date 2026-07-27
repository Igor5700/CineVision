from __future__ import annotations

from movielib.domain.entities.rating import Rating
from movielib.domain.ports.rating_repository import RatingRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class ListMyRatings:
    def __init__(self, ratings: RatingRepository) -> None:
        self._ratings = ratings

    async def __call__(self, telegram_id: TelegramId) -> list[Rating]:
        return await self._ratings.list_my_ratings(telegram_id)
