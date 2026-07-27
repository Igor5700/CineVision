from __future__ import annotations

from movielib.domain.ports.review_repository import ReviewRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class DeleteReview:
    def __init__(self, reviews: ReviewRepository) -> None:
        self._reviews = reviews

    async def __call__(self, telegram_id: TelegramId, film_id: int) -> None:
        await self._reviews.delete(telegram_id, film_id)
