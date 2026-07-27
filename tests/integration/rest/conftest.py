from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from movielib.bootstrap.config import Settings
from movielib.bootstrap.container import Container, build_container
from movielib.presentation.rest.app import create_app


@pytest.fixture()
def rest_settings(sqlite_url: str) -> Settings:
    return Settings(
        bot_token="123456:AAEfake-token-for-tests-only",
        films_api_token="token",
        database_url=sqlite_url,
    )


@pytest.fixture()
def client(rest_settings: Settings) -> Iterator[TestClient]:
    app = create_app(rest_settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture()
async def seed_container(rest_settings: Settings) -> AsyncIterator[Container]:
    built = build_container(rest_settings)
    try:
        yield built
    finally:
        await built.engine.dispose()
