"""Схеми авторизації."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: EmailStr = Field(examples=["admin@courier.ua"])
    password: str = Field(min_length=1, max_length=128, examples=["Password123!"])


class TokenResponse(BaseModel):
    """Відповідь на успішний вхід або реєстрацію."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Час життя токена в секундах")
    user: UserRead
