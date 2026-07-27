from __future__ import annotations

from dataclasses import replace

from movielib.domain.entities.collection import Collection
from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId


class FakeCollectionRepository:
    def __init__(self, films_by_id: dict[int, Film] | None = None) -> None:
        self._films_by_id = films_by_id if films_by_id is not None else {}
        self._collections: dict[int, Collection] = {}
        self._items: dict[int, list[int]] = {}
        self._next_id = 1

    async def create(self, collection: Collection) -> Collection:
        created = replace(collection, id=self._next_id)
        self._collections[self._next_id] = created
        self._items[self._next_id] = []
        self._next_id += 1
        return created

    async def get(self, collection_id: int) -> Collection | None:
        return self._collections.get(collection_id)

    async def list_for_user(self, telegram_id: TelegramId) -> list[Collection]:
        matches = [c for c in self._collections.values() if int(c.telegram_id) == int(telegram_id)]
        return sorted(matches, key=lambda c: c.created_at, reverse=True)

    async def delete(self, collection_id: int) -> None:
        self._collections.pop(collection_id, None)
        self._items.pop(collection_id, None)

    async def add_film(self, collection_id: int, film_id: int) -> None:
        items = self._items.setdefault(collection_id, [])
        if film_id not in items:
            items.append(film_id)

    async def remove_film(self, collection_id: int, film_id: int) -> None:
        items = self._items.get(collection_id, [])
        if film_id in items:
            items.remove(film_id)

    async def list_films(self, collection_id: int) -> list[Film]:
        film_ids = self._items.get(collection_id, [])
        return [self._films_by_id[fid] for fid in film_ids if fid in self._films_by_id]
