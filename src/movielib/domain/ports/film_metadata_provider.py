from __future__ import annotations

from typing import Protocol

from movielib.domain.entities.film import Film


class FilmMetadataProvider(Protocol):
    async def search_by_name(self, name: str) -> list[Film]: ...

    async def get_by_id(self, film_id: int) -> Film | None: ...
