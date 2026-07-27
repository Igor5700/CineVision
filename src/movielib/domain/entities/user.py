from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from movielib.domain.value_objects.balance import Balance
from movielib.domain.value_objects.telegram_id import TelegramId


@dataclass(slots=True)
class User:
    telegram_id: TelegramId
    username: str | None
    balance: Balance
    registered_at: datetime
    birthday: date | None = None
