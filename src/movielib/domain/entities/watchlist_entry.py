from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from movielib.domain.value_objects.telegram_id import TelegramId


@dataclass(slots=True)
class WatchlistEntry:
    telegram_id: TelegramId
    film_id: int
    added_at: datetime
