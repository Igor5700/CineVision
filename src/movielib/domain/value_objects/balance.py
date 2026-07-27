from __future__ import annotations

from dataclasses import dataclass

from movielib.domain.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class Balance:
    amount: int = 0

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise DomainValidationError(f"Balance cannot be negative, got {self.amount}")

    def __int__(self) -> int:
        return self.amount
