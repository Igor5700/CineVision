from __future__ import annotations

from movielib.domain.entities.review import Review
from movielib.domain.ports.review_repository import ReviewRepository


class ListFilmReviews:
    def __init__(self, reviews: ReviewRepository) -> None:
        self._reviews = reviews

    async def __call__(self, film_id: int, *, limit: int = 20) -> list[Review]:
        return await self._reviews.list_for_film(film_id, limit=limit)
