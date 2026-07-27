from __future__ import annotations

from typing import Protocol

from movielib.domain.entities.film import Film


class FilmRepository(Protocol):
    async def get(self, film_id: int) -> Film | None: ...

    async def search_by_title(self, query: str, *, limit: int = 10) -> list[Film]: ...

    async def upsert_many(self, films: list[Film]) -> None: ...
