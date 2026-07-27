from __future__ import annotations

from datetime import date, datetime


class FakeClock:
    def __init__(self, fixed_now: datetime) -> None:
        self._fixed_now = fixed_now

    def now(self) -> datetime:
        return self._fixed_now

    def today(self) -> date:
        return self._fixed_now.date()
