from __future__ import annotations

from movielib.application.authorization import ensure_owner
from movielib.domain.errors import CollectionNotFoundError
from movielib.domain.ports.collection_repository import CollectionRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class AddFilmToCollection:
    def __init__(self, collections: CollectionRepository) -> None:
        self._collections = collections

    async def __call__(self, telegram_id: TelegramId, collection_id: int, film_id: int) -> None:
        collection = await self._collections.get(collection_id)
        if collection is None:
            raise CollectionNotFoundError(collection_id)
        ensure_owner(telegram_id, collection.telegram_id)
        await self._collections.add_film(collection_id, film_id)
