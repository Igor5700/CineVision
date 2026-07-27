from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.collection import Collection
from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.film_repository_sqlalchemy import film_to_entity
from movielib.infrastructure.persistence.models import (
    CollectionItemModel,
    CollectionModel,
    FilmModel,
)


class SqlAlchemyCollectionRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, collection: Collection) -> Collection:
        async with self._session_factory() as session:
            model = CollectionModel(
                telegram_id=int(collection.telegram_id),
                name=collection.name,
                description=collection.description,
                created_at=collection.created_at,
            )
            session.add(model)
            await session.commit()
            return _to_entity(model)

    async def get(self, collection_id: int) -> Collection | None:
        async with self._session_factory() as session:
            model = await session.get(CollectionModel, collection_id)
            return _to_entity(model) if model is not None else None

    async def list_for_user(self, telegram_id: TelegramId) -> list[Collection]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CollectionModel)
                .where(CollectionModel.telegram_id == int(telegram_id))
                .order_by(CollectionModel.created_at.desc())
            )
            return [_to_entity(model) for model in result.scalars()]

    async def delete(self, collection_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(CollectionModel, collection_id)
            if model is not None:
                await session.delete(model)
                await session.commit()

    async def add_film(self, collection_id: int, film_id: int) -> None:
        async with self._session_factory() as session:
            existing = await session.get(CollectionItemModel, (collection_id, film_id))
            if existing is None:
                session.add(
                    CollectionItemModel(
                        collection_id=collection_id, film_id=film_id, added_at=datetime.now(UTC)
                    )
                )
                await session.commit()

    async def remove_film(self, collection_id: int, film_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(CollectionItemModel, (collection_id, film_id))
            if model is not None:
                await session.delete(model)
                await session.commit()

    async def list_films(self, collection_id: int) -> list[Film]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FilmModel)
                .join(CollectionItemModel, FilmModel.id == CollectionItemModel.film_id)
                .where(CollectionItemModel.collection_id == collection_id)
                .order_by(CollectionItemModel.added_at.desc())
            )
            return [film_to_entity(model) for model in result.scalars()]


def _to_entity(model: CollectionModel) -> Collection:
    return Collection(
        id=model.id,
        telegram_id=TelegramId(model.telegram_id),
        name=model.name,
        description=model.description,
        created_at=model.created_at,
    )
