"""Хешування паролів і робота з JWT access token."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

#: Максимальна довжина пароля в байтах, яку приймає bcrypt.
_BCRYPT_MAX_BYTES = 72


def _truncate_for_bcrypt(password: str) -> bytes:
    """bcrypt мовчки ігнорує все після 72 байтів, тож обрізаємо явно."""
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """Повертає bcrypt-хеш пароля. Відкритий пароль ніде не зберігається."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(_truncate_for_bcrypt(password), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Перевіряє пароль проти збереженого хеша."""
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(_truncate_for_bcrypt(plain_password), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str | int,
    role: str,
    expires_minutes: int | None = None,
) -> str:
    """Створює підписаний JWT access token."""
    expire_delta = timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + expire_delta).timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Розбирає JWT. Повертає None, якщо токен недійсний або прострочений."""
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    return payload


def access_token_expires_in_seconds() -> int:
    """Час життя токена в секундах - зручно віддавати клієнту."""
    return settings.access_token_expire_minutes * 60
