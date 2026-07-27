from __future__ import annotations

from movielib.domain.entities.rating import Rating
from movielib.domain.ports.rating_repository import RatingRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class GetMyRating:
    def __init__(self, ratings: RatingRepository) -> None:
        self._ratings = ratings

    async def __call__(self, telegram_id: TelegramId, film_id: int) -> Rating | None:
        return await self._ratings.get_my_rating(telegram_id, film_id)
