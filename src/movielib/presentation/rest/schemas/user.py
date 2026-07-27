from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from movielib.domain.entities.user import User


class RegisterUserRequest(BaseModel):
    telegram_id: int = Field(gt=0)
    username: str | None = None


class UpdateDisplayNameRequest(BaseModel):
    display_name: str = Field(min_length=1)


class SetBirthdayRequest(BaseModel):
    birthday: str = Field(min_length=1, description="dd.mm.yyyy, e.g. 15.06.1995")


class UserResponse(BaseModel):
    telegram_id: int
    username: str | None
    balance: int
    registered_at: datetime
    birthday: date | None

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            telegram_id=int(user.telegram_id),
            username=user.username,
            balance=int(user.balance),
            registered_at=user.registered_at,
            birthday=user.birthday,
        )
