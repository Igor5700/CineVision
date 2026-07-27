from __future__ import annotations

from movielib.domain.entities.collection import Collection
from movielib.domain.ports.collection_repository import CollectionRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class ListMyCollections:
    def __init__(self, collections: CollectionRepository) -> None:
        self._collections = collections

    async def __call__(self, telegram_id: TelegramId) -> list[Collection]:
        return await self._collections.list_for_user(telegram_id)
