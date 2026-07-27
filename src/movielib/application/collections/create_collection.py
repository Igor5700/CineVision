from __future__ import annotations

from movielib.domain.entities.collection import Collection
from movielib.domain.ports.clock import Clock
from movielib.domain.ports.collection_repository import CollectionRepository
from movielib.domain.value_objects.telegram_id import TelegramId


class CreateCollection:
    def __init__(self, collections: CollectionRepository, clock: Clock) -> None:
        self._collections = collections
        self._clock = clock

    async def __call__(
        self, telegram_id: TelegramId, name: str, description: str | None = None
    ) -> Collection:
        collection = Collection(
            id=None,
            telegram_id=telegram_id,
            name=name,
            description=description,
            created_at=self._clock.now(),
        )
        return await self._collections.create(collection)
