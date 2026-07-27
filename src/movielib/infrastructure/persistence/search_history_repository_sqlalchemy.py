from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.models import SearchHistoryModel


class SqlAlchemySearchHistoryRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def log(self, telegram_id: TelegramId, query: str) -> None:
        async with self._session_factory() as session:
            session.add(
                SearchHistoryModel(
                    telegram_id=int(telegram_id), query=query, searched_at=datetime.now(UTC)
                )
            )
            await session.commit()

    async def list_recent(self, telegram_id: TelegramId, *, limit: int = 10) -> list[str]:
        async with self._session_factory() as session:
            latest = func.max(SearchHistoryModel.searched_at)
            result = await session.execute(
                select(SearchHistoryModel.query)
                .where(SearchHistoryModel.telegram_id == int(telegram_id))
                .group_by(SearchHistoryModel.query)
                .order_by(latest.desc())
                .limit(limit)
            )
            return list(result.scalars())
