"""Ендпоінти управління користувачами."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import CurrentUser, DbSession, PageParamsDep, make_sort_dependency, require_roles
from app.core.enums import UserRole
from app.core.pagination import MAX_PAGE_SIZE, PageParams, SortParams
from app.models.user import User
from app.repositories.user_repository import USER_SORT_FIELDS
from app.schemas.common import ErrorResponse, PageMeta, PaginatedResponse
from app.schemas.user import (
    UserCreate,
    UserProfileUpdate,
    UserRead,
    UserShort,
    UserStatusUpdate,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

UserSortDep = Annotated[
    SortParams,
    Depends(make_sort_dependency(set(USER_SORT_FIELDS), "created_at")),
]

AdminOnly = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
StaffOnly = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER))]


@router.get(
    "",
    response_model=PaginatedResponse[UserRead],
    summary="Список користувачів",
    description="Пошук за іменем, email або телефоном, фільтри за роллю і статусом, "
    "серверна пагінація та сортування. Доступно ролі ADMIN.",
    responses={403: {"model": ErrorResponse}},
)
def list_users(
    session: DbSession,
    _: AdminOnly,
    page_params: PageParamsDep,
    sort: UserSortDep,
    search: Annotated[
        str | None, Query(max_length=120, description="Ім'я, email або телефон")
    ] = None,
    role: Annotated[UserRole | None, Query(description="Фільтр за роллю")] = None,
    is_active: Annotated[bool | None, Query(description="Фільтр за статусом")] = None,
) -> PaginatedResponse[UserRead]:
    result = UserService(session).list_users(
        page=page_params, sort=sort, search=search, role=role, is_active=is_active
    )
    return PaginatedResponse[UserRead](
        items=[UserRead.model_validate(user) for user in result.items],
        meta=PageMeta(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
            total_pages=result.total_pages,
        ),
    )


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити користувача",
    description="Доступно лише ролі ADMIN.",
    responses={403: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def create_user(payload: UserCreate, session: DbSession, _: AdminOnly) -> UserRead:
    return UserRead.model_validate(UserService(session).create_user(payload))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Власний профіль",
)
def read_own_profile(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Оновити власний профіль",
    description="Користувач може змінити ім'я, прізвище, телефон і пароль. Роль і email - ні.",
)
def update_own_profile(
    payload: UserProfileUpdate, session: DbSession, current_user: CurrentUser
) -> UserRead:
    return UserRead.model_validate(UserService(session).update_profile(current_user, payload))


@router.get(
    "/customers",
    response_model=list[UserShort],
    summary="Активні клієнти для вибору у формі замовлення",
    description="Потрібно диспетчеру й адміністратору, щоб оформити замовлення "
    "від імені клієнта. Доступно ролям ADMIN, DISPATCHER.",
    responses={403: {"model": ErrorResponse}},
)
def list_customer_options(
    session: DbSession,
    _: StaffOnly,
    search: Annotated[str | None, Query(max_length=120)] = None,
) -> list[UserShort]:
    result = UserService(session).list_users(
        page=PageParams(page=1, page_size=MAX_PAGE_SIZE),
        sort=SortParams(sort_by="last_name", sort_order="asc"),
        search=search,
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    return [UserShort.model_validate(user) for user in result.items]


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Користувач за id",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_user(
    session: DbSession,
    current_user: CurrentUser,
    user_id: Annotated[int, Path(ge=1)],
) -> UserRead:
    return UserRead.model_validate(
        UserService(session).get_user(user_id, requester=current_user)
    )


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Редагувати користувача",
    description="Доступно лише ролі ADMIN.",
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def update_user(
    payload: UserUpdate,
    session: DbSession,
    admin: AdminOnly,
    user_id: Annotated[int, Path(ge=1)],
) -> UserRead:
    return UserRead.model_validate(
        UserService(session).update_user(user_id, payload, requester=admin)
    )


@router.patch(
    "/{user_id}/status",
    response_model=UserRead,
    summary="Заблокувати або активувати користувача",
    description="Доступно лише ролі ADMIN.",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def set_user_status(
    payload: UserStatusUpdate,
    session: DbSession,
    admin: AdminOnly,
    user_id: Annotated[int, Path(ge=1)],
) -> UserRead:
    return UserRead.model_validate(
        UserService(session).set_status(user_id, payload, requester=admin)
    )
