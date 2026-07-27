from __future__ import annotations

from movielib.domain.entities.review import Review
from movielib.domain.ports.clock import Clock
from movielib.domain.ports.review_repository import ReviewRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class WriteReview:
    def __init__(self, reviews: ReviewRepository, clock: Clock) -> None:
        self._reviews = reviews
        self._clock = clock

    async def __call__(self, telegram_id: TelegramId, film_id: int, text: str) -> None:
        existing = await self._reviews.get(telegram_id, film_id)
        now = self._clock.now()
        review = Review(
            telegram_id=telegram_id,
            film_id=film_id,
            text=text,
            created_at=existing.created_at if existing is not None else now,
            updated_at=now,
        )
        await self._reviews.upsert(review)
