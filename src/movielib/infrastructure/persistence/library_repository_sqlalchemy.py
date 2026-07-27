from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.film_repository_sqlalchemy import film_to_entity
from movielib.infrastructure.persistence.models import (
    FavoriteModel,
    FilmModel,
    ViewingHistoryModel,
    WatchlistModel,
)


class SqlAlchemyLibraryRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def add_to_watchlist(self, telegram_id: TelegramId, film_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(WatchlistModel, (int(telegram_id), film_id))
            if model is None:
                session.add(
                    WatchlistModel(
                        telegram_id=int(telegram_id), film_id=film_id, added_at=datetime.now(UTC)
                    )
                )
            else:
                model.added_at = datetime.now(UTC)
            await session.commit()

    async def remove_from_watchlist(self, telegram_id: TelegramId, film_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(WatchlistModel, (int(telegram_id), film_id))
            if model is not None:
                await session.delete(model)
                await session.commit()

    async def list_watchlist(self, telegram_id: TelegramId) -> list[Film]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FilmModel)
                .join(WatchlistModel, FilmModel.id == WatchlistModel.film_id)
                .where(WatchlistModel.telegram_id == int(telegram_id))
                .order_by(WatchlistModel.added_at.desc())
            )
            return [film_to_entity(model) for model in result.scalars()]

    async def add_favorite(self, telegram_id: TelegramId, film_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(FavoriteModel, (int(telegram_id), film_id))
            if model is None:
                session.add(
                    FavoriteModel(
                        telegram_id=int(telegram_id), film_id=film_id, added_at=datetime.now(UTC)
                    )
                )
            else:
                model.added_at = datetime.now(UTC)
            await session.commit()

    async def remove_favorite(self, telegram_id: TelegramId, film_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(FavoriteModel, (int(telegram_id), film_id))
            if model is not None:
                await session.delete(model)
                await session.commit()

    async def list_favorites(self, telegram_id: TelegramId) -> list[Film]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FilmModel)
                .join(FavoriteModel, FilmModel.id == FavoriteModel.film_id)
                .where(FavoriteModel.telegram_id == int(telegram_id))
                .order_by(FavoriteModel.added_at.desc())
            )
            return [film_to_entity(model) for model in result.scalars()]

    async def mark_watched(self, telegram_id: TelegramId, film_id: int) -> None:
        async with self._session_factory() as session:
            model = await session.get(ViewingHistoryModel, (int(telegram_id), film_id))
            if model is None:
                session.add(
                    ViewingHistoryModel(
                        telegram_id=int(telegram_id), film_id=film_id, watched_at=datetime.now(UTC)
                    )
                )
            else:
                model.watched_at = datetime.now(UTC)
            await session.commit()

    async def list_history(self, telegram_id: TelegramId, *, limit: int = 20) -> list[Film]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(FilmModel)
                .join(ViewingHistoryModel, FilmModel.id == ViewingHistoryModel.film_id)
                .where(ViewingHistoryModel.telegram_id == int(telegram_id))
                .order_by(ViewingHistoryModel.watched_at.desc())
                .limit(limit)
            )
            return [film_to_entity(model) for model in result.scalars()]

    async def count_history(self, telegram_id: TelegramId) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count())
                .select_from(ViewingHistoryModel)
                .where(ViewingHistoryModel.telegram_id == int(telegram_id))
            )
            return result.scalar_one()
