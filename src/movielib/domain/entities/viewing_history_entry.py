from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from movielib.domain.value_objects.telegram_id import TelegramId


@dataclass(slots=True)
class ViewingHistoryEntry:
    telegram_id: TelegramId
    film_id: int
    watched_at: datetime
