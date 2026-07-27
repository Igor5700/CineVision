from __future__ import annotations

from movielib.domain.entities.review import Review
from movielib.domain.value_objects.telegram_id import TelegramId


class FakeReviewRepository:
    def __init__(self) -> None:
        self._reviews: dict[tuple[int, int], Review] = {}

    async def upsert(self, review: Review) -> None:
        self._reviews[(int(review.telegram_id), review.film_id)] = review

    async def get(self, telegram_id: TelegramId, film_id: int) -> Review | None:
        return self._reviews.get((int(telegram_id), film_id))

    async def delete(self, telegram_id: TelegramId, film_id: int) -> None:
        self._reviews.pop((int(telegram_id), film_id), None)

    async def list_for_film(self, film_id: int, *, limit: int = 20) -> list[Review]:
        matches = [r for (_, fid), r in self._reviews.items() if fid == film_id]
        matches.sort(key=lambda r: r.created_at, reverse=True)
        return matches[:limit]
