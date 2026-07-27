from __future__ import annotations

from dataclasses import dataclass

from movielib.domain.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class TelegramId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise DomainValidationError(f"Telegram id must be positive, got {self.value}")

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)
