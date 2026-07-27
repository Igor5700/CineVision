from __future__ import annotations

from movielib.domain.entities.rating import Rating
from movielib.domain.value_objects.telegram_id import TelegramId


class FakeRatingRepository:
    def __init__(self) -> None:
        self._ratings: dict[tuple[int, int], Rating] = {}

    async def rate(self, rating: Rating) -> None:
        self._ratings[(int(rating.telegram_id), rating.film_id)] = rating

    async def get_my_rating(self, telegram_id: TelegramId, film_id: int) -> Rating | None:
        return self._ratings.get((int(telegram_id), film_id))

    async def list_my_ratings(self, telegram_id: TelegramId) -> list[Rating]:
        matches = [r for (uid, _), r in self._ratings.items() if uid == int(telegram_id)]
        return sorted(matches, key=lambda r: r.rated_at, reverse=True)

    async def average_for_film(self, film_id: int) -> float | None:
        scores = [r.score for (_, fid), r in self._ratings.items() if fid == film_id]
        return sum(scores) / len(scores) if scores else None
