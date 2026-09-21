"""Ендпоінти авторизації."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import ErrorResponse, MessageResponse
from app.schemas.user import UserRead, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Реєстрація клієнта",
    responses={409: {"model": ErrorResponse, "description": "Email уже використовується"}},
)
def register(payload: UserRegister, session: DbSession) -> TokenResponse:
    """Створює обліковий запис клієнта і одразу повертає access token."""
    return AuthService(session).register_customer(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вхід за email і паролем",
    responses={
        401: {"model": ErrorResponse, "description": "Неправильний email або пароль"},
        403: {"model": ErrorResponse, "description": "Обліковий запис заблоковано"},
    },
)
def login(payload: LoginRequest, session: DbSession) -> TokenResponse:
    return AuthService(session).login(payload.email, payload.password)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Дані поточного користувача",
    responses={401: {"model": ErrorResponse}},
)
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Вихід із системи",
)
def logout(current_user: CurrentUser) -> MessageResponse:
    """Вихід.

    Access token не має серверного стану, тож клієнт просто видаляє його
    в себе. Ендпоінт існує, щоб frontend мав єдину точку виходу, а в
    наступних частинах сюди можна додати чорний список токенів.
    """
    return MessageResponse(message="Ви вийшли із системи")
