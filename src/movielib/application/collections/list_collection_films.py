from __future__ import annotations

from movielib.domain.entities.film import Film
from movielib.domain.errors import CollectionNotFoundError
from movielib.domain.ports.collection_repository import CollectionRepository


class ListCollectionFilms:
    def __init__(self, collections: CollectionRepository) -> None:
        self._collections = collections

    async def __call__(self, collection_id: int) -> list[Film]:
        collection = await self._collections.get(collection_id)
        if collection is None:
            raise CollectionNotFoundError(collection_id)
        return await self._collections.list_films(collection_id)
