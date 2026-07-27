from __future__ import annotations

import pytest
from pydantic import ValidationError

from movielib.bootstrap.config import Settings


def test_database_url_has_a_sensible_default() -> None:
    settings = Settings(bot_token="123:abc", films_api_token="token")

    assert settings.database_url == "sqlite+aiosqlite:///data/movielib.db"


def test_database_url_can_be_overridden() -> None:
    settings = Settings(
        bot_token="123:abc",
        films_api_token="token",
        database_url="postgresql+asyncpg://localhost/movielib",
    )

    assert settings.database_url == "postgresql+asyncpg://localhost/movielib"


@pytest.mark.parametrize("field", ["bot_token", "films_api_token"])
def test_rejects_a_blank_required_field(field: str) -> None:
    values = {"bot_token": "123:abc", "films_api_token": "token"}
    values[field] = ""

    with pytest.raises(ValidationError):
        Settings(**values)
