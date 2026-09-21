"""Бізнес-логіка управління користувачами."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.errors import (
    BusinessRuleError,
    EmailAlreadyUsedError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.pagination import Page, PageParams, SortParams
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserProfileUpdate, UserStatusUpdate, UserUpdate

#: Ролі, яким дозволено переглядати список усіх користувачів.
USER_READ_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN, UserRole.MANAGER})

#: Ролі, яким дозволено створювати й редагувати користувачів.
USER_WRITE_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN})


class UserService:
    """Операції над обліковими записами."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    # --- Читання ---

    def list_users(
        self,
        *,
        page: PageParams,
        sort: SortParams,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> Page[User]:
        return self.users.list_users(
            page=page, sort=sort, search=search, role=role, is_active=is_active
        )

    def get_user(self, user_id: int, *, requester: User) -> User:
        """Користувач може дивитися себе; ADMIN і MANAGER - будь-кого."""
        if requester.id != user_id and requester.role not in USER_READ_ROLES:
            raise PermissionDeniedError("Ви можете переглядати лише власний профіль")
        user = self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Користувача не знайдено", code="USER_NOT_FOUND")
        return user

    def get_required(self, user_id: int) -> User:
        user = self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Користувача не знайдено", code="USER_NOT_FOUND")
        return user

    # --- Запис ---

    def create_user(self, payload: UserCreate) -> User:
        if self.users.email_exists(payload.email):
            raise EmailAlreadyUsedError()

        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email.lower(),
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            role=payload.role,
            is_active=payload.is_active,
        )
        self.users.add(user)
        self.users.commit()
        self.session.refresh(user)
        return user

    def update_user(self, user_id: int, payload: UserUpdate, *, requester: User) -> User:
        user = self.get_required(user_id)
        data = payload.model_dump(exclude_unset=True)

        if "email" in data and data["email"]:
            new_email = str(data["email"]).lower()
            if self.users.email_exists(new_email, exclude_user_id=user.id):
                raise EmailAlreadyUsedError()
            user.email = new_email

        if "role" in data and data["role"] is not None:
            new_role = UserRole(data["role"])
            # Адміністратор не може випадково зняти роль сам із себе і
            # залишити систему без жодного адміністратора.
            if user.id == requester.id and new_role != UserRole.ADMIN:
                raise BusinessRuleError("Не можна змінити власну роль адміністратора")
            user.role = new_role

        for field in ("first_name", "last_name", "phone"):
            if field in data and data[field] is not None:
                setattr(user, field, data[field])

        if data.get("password"):
            user.password_hash = hash_password(str(data["password"]))

        self.users.commit()
        self.session.refresh(user)
        return user

    def update_profile(self, user: User, payload: UserProfileUpdate) -> User:
        """Редагування власного профілю: без ролі й без email."""
        data = payload.model_dump(exclude_unset=True)
        for field in ("first_name", "last_name", "phone"):
            if field in data and data[field] is not None:
                setattr(user, field, data[field])
        if data.get("password"):
            user.password_hash = hash_password(str(data["password"]))
        self.users.commit()
        self.session.refresh(user)
        return user

    def set_status(self, user_id: int, payload: UserStatusUpdate, *, requester: User) -> User:
        """Блокування або активація облікового запису."""
        user = self.get_required(user_id)
        if user.id == requester.id and not payload.is_active:
            raise BusinessRuleError("Не можна заблокувати власний обліковий запис")
        user.is_active = payload.is_active
        self.users.commit()
        self.session.refresh(user)
        return user
