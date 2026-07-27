from __future__ import annotations

from movielib.domain.ports.rating_repository import RatingRepository


class GetAverageRating:
    def __init__(self, ratings: RatingRepository) -> None:
        self._ratings = ratings

    async def __call__(self, film_id: int) -> float | None:
        return await self._ratings.average_for_film(film_id)
