from __future__ import annotations

from movielib.domain.entities.review import Review
from movielib.domain.ports.review_repository import ReviewRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class GetMyReview:
    def __init__(self, reviews: ReviewRepository) -> None:
        self._reviews = reviews

    async def __call__(self, telegram_id: TelegramId, film_id: int) -> Review | None:
        return await self._reviews.get(telegram_id, film_id)
