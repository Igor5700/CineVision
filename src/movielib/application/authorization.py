from __future__ import annotations

from movielib.domain.errors import NotAuthorizedError
from movielib.domain.value_objects.telegram_id import TelegramId


def ensure_owner(telegram_id: TelegramId, owner_id: TelegramId) -> None:
    if telegram_id != owner_id:
        raise NotAuthorizedError(int(telegram_id))
