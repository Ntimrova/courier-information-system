"""Залежності FastAPI: сесія БД, поточний користувач, перевірка ролей.

Права перевіряються саме тут - на backend. Приховані кнопки на frontend
це лише зручність, а не захист.
"""

from __future__ import annotations

from collections.abc import Callable, Generator, Iterable
from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.errors import AuthenticationError, InactiveUserError, PermissionDeniedError
from app.core.pagination import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PageParams,
    SortParams,
)
from app.core.security import decode_access_token
from app.database.session import get_session
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False, description="JWT access token")


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> User:
    """Дістає користувача з JWT і перевіряє, що він не заблокований."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Потрібен токен доступу")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise AuthenticationError("Токен недійсний або прострочений", code="INVALID_TOKEN")

    raw_subject = payload.get("sub")
    try:
        user_id = int(raw_subject)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise AuthenticationError("Токен недійсний", code="INVALID_TOKEN") from None

    user = UserRepository(session).get_by_id(user_id)
    if user is None:
        raise AuthenticationError("Користувача не знайдено", code="INVALID_TOKEN")
    if not user.is_active:
        raise InactiveUserError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Фабрика залежності «тільки для цих ролей»."""

    allowed: frozenset[UserRole] = frozenset(roles)

    def _dependency(current_user: CurrentUser) -> User:
        if current_user.role not in allowed:
            raise PermissionDeniedError(
                "Недостатньо прав для цієї дії. "
                f"Потрібна роль: {', '.join(sorted(role.value for role in allowed))}"
            )
        return current_user

    return _dependency


def require_any_role(roles: Iterable[UserRole]) -> Callable[[User], User]:
    return require_roles(*roles)


def get_page_params(
    page: Annotated[int, Query(ge=1, description="Номер сторінки")] = DEFAULT_PAGE,
    page_size: Annotated[
        int, Query(ge=1, le=MAX_PAGE_SIZE, description="Записів на сторінку")
    ] = DEFAULT_PAGE_SIZE,
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


PageParamsDep = Annotated[PageParams, Depends(get_page_params)]


def make_sort_dependency(
    allowed_fields: set[str], default_field: str
) -> Callable[..., SortParams]:
    """Створює залежність сортування з білим списком полів.

    Білий список потрібен, щоб у ORDER BY не потрапив довільний рядок
    від клієнта.
    """

    description = "Поле сортування: " + ", ".join(sorted(allowed_fields))

    def _dependency(
        sort_by: str = Query(default_field, description=description),
        sort_order: str = Query("desc", pattern="^(asc|desc)$", description="asc або desc"),
    ) -> SortParams:
        field = sort_by if sort_by in allowed_fields else default_field
        return SortParams(sort_by=field, sort_order=sort_order)

    return _dependency
