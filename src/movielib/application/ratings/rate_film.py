from __future__ import annotations

from movielib.domain.entities.rating import Rating
from movielib.domain.ports.clock import Clock
from movielib.domain.ports.rating_repository import RatingRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class RateFilm:
    def __init__(self, ratings: RatingRepository, clock: Clock) -> None:
        self._ratings = ratings
        self._clock = clock

    async def __call__(self, telegram_id: TelegramId, film_id: int, score: int) -> None:
        rating = Rating(
            telegram_id=telegram_id, film_id=film_id, score=score, rated_at=self._clock.now()
        )
        await self._ratings.rate(rating)
