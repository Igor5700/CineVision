from __future__ import annotations

from fastapi import APIRouter, Depends

from movielib.bootstrap.container import UseCases
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.rest.dependencies import get_use_cases
from movielib.presentation.rest.schemas.user import (
    RegisterUserRequest,
    SetBirthdayRequest,
    UpdateDisplayNameRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
async def register_user(
    body: RegisterUserRequest, use_cases: UseCases = Depends(get_use_cases)
) -> UserResponse:
    user = await use_cases.users.register(TelegramId(body.telegram_id), body.username)
    return UserResponse.from_domain(user)


@router.get("/{telegram_id}", response_model=UserResponse)
async def get_profile(
    telegram_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> UserResponse:
    user = await use_cases.users.get_profile(TelegramId(telegram_id))
    return UserResponse.from_domain(user)


@router.put("/{telegram_id}/display-name", response_model=UserResponse)
async def update_display_name(
    telegram_id: int,
    body: UpdateDisplayNameRequest,
    use_cases: UseCases = Depends(get_use_cases),
) -> UserResponse:
    await use_cases.users.update_display_name(TelegramId(telegram_id), body.display_name)
    user = await use_cases.users.get_profile(TelegramId(telegram_id))
    return UserResponse.from_domain(user)


@router.put("/{telegram_id}/birthday", response_model=UserResponse)
async def set_birthday(
    telegram_id: int, body: SetBirthdayRequest, use_cases: UseCases = Depends(get_use_cases)
) -> UserResponse:
    await use_cases.users.set_birthday(TelegramId(telegram_id), body.birthday)
    user = await use_cases.users.get_profile(TelegramId(telegram_id))
    return UserResponse.from_domain(user)
