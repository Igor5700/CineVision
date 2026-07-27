from __future__ import annotations

from movielib.domain.entities.film import Film


class FakeFilmMetadataProvider:
    def __init__(self, results: list[Film] | None = None) -> None:
        self.results = results if results is not None else []
        self.queries: list[str] = []
        self.by_id: dict[int, Film] = {film.id: film for film in self.results}

    async def search_by_name(self, name: str) -> list[Film]:
        self.queries.append(name)
        return self.results

    async def get_by_id(self, film_id: int) -> Film | None:
        return self.by_id.get(film_id)
