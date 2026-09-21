"""Бізнес-логіка авторизації: реєстрація, вхід, поточний користувач."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.errors import (
    EmailAlreadyUsedError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.core.security import (
    access_token_expires_in_seconds,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserRead, UserRegister


class AuthService:
    """Реєстрація та вхід користувачів."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def register_customer(self, payload: UserRegister) -> TokenResponse:
        """Самостійна реєстрація клієнта.

        Роль завжди CUSTOMER: підвищити її може лише адміністратор.
        """
        if self.users.email_exists(payload.email):
            raise EmailAlreadyUsedError()

        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email.lower(),
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        self.users.add(user)
        self.users.commit()
        self.session.refresh(user)
        return self._build_token_response(user)

    def login(self, email: str, password: str) -> TokenResponse:
        """Вхід за email і паролем."""
        user = self.users.get_by_email(email)

        # Одне й те саме повідомлення для невідомого email і неправильного
        # пароля: інакше форма входу підказувала б, які адреси зареєстровані.
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        return self._build_token_response(user)

    @staticmethod
    def _build_token_response(user: User) -> TokenResponse:
        token = create_access_token(subject=user.id, role=user.role.value)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=access_token_expires_in_seconds(),
            user=UserRead.model_validate(user),
        )
