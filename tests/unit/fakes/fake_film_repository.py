from __future__ import annotations

from movielib.domain.entities.film import Film


class FakeFilmRepository:
    def __init__(self) -> None:
        self._films: dict[int, Film] = {}

    async def get(self, film_id: int) -> Film | None:
        return self._films.get(film_id)

    async def search_by_title(self, query: str, *, limit: int = 10) -> list[Film]:
        needle = query.strip().lower()
        matches = [film for film in self._films.values() if needle in film.title.lower()]
        return matches[:limit]

    async def upsert_many(self, films: list[Film]) -> None:
        for film in films:
            self._films[film.id] = film
