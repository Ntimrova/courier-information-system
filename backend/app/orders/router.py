"""Ендпоінти замовлень."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import CurrentUser, DbSession, PageParamsDep, make_sort_dependency
from app.core.enums import DeliveryType, OrderStatus
from app.core.pagination import SortParams
from app.repositories.order_repository import ORDER_SORT_FIELDS
from app.schemas.common import ErrorResponse, PageMeta, PaginatedResponse
from app.schemas.order import (
    OrderCancel,
    OrderCreate,
    OrderListItem,
    OrderRead,
    OrderStatusChange,
    OrderStatusHistoryRead,
    OrderUpdate,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

OrderSortDep = Annotated[
    SortParams,
    Depends(make_sort_dependency(set(ORDER_SORT_FIELDS), "created_at")),
]


@router.get(
    "",
    response_model=PaginatedResponse[OrderListItem],
    summary="Список замовлень",
    description="ADMIN і DISPATCHER бачать усі замовлення, CUSTOMER - лише власні. "
    "Пошук за tracking number, телефоном або ім'ям, фільтри за статусом, типом доставки "
    "і датою, серверна пагінація та сортування.",
)
def list_orders(
    session: DbSession,
    current_user: CurrentUser,
    page_params: PageParamsDep,
    sort: OrderSortDep,
    search: Annotated[
        str | None, Query(max_length=120, description="Tracking number, телефон або ім'я")
    ] = None,
    order_status: Annotated[
        OrderStatus | None, Query(alias="status", description="Фільтр за статусом")
    ] = None,
    delivery_type: Annotated[
        DeliveryType | None, Query(description="Фільтр за типом доставки")
    ] = None,
    date_from: Annotated[date | None, Query(description="Бажана дата доставки від")] = None,
    date_to: Annotated[date | None, Query(description="Бажана дата доставки до")] = None,
    customer_id: Annotated[
        int | None, Query(ge=1, description="Фільтр за клієнтом (ігнорується для CUSTOMER)")
    ] = None,
) -> PaginatedResponse[OrderListItem]:
    result = OrderService(session).list_orders(
        user=current_user,
        page=page_params,
        sort=sort,
        search=search,
        status=order_status,
        delivery_type=delivery_type,
        date_from=date_from,
        date_to=date_to,
        customer_id=customer_id,
    )
    return PaginatedResponse[OrderListItem](
        items=[OrderListItem.model_validate(order) for order in result.items],
        meta=PageMeta(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
            total_pages=result.total_pages,
        ),
    )


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити замовлення",
    description="CUSTOMER створює замовлення для себе. ADMIN і DISPATCHER мусять указати "
    "`customer_id` клієнта, від імені якого оформлюється замовлення.",
    responses={403: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_order(payload: OrderCreate, session: DbSession, current_user: CurrentUser) -> OrderRead:
    return OrderRead.model_validate(
        OrderService(session).create_order(payload, user=current_user)
    )


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Замовлення за id",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_order(
    session: DbSession,
    current_user: CurrentUser,
    order_id: Annotated[int, Path(ge=1)],
) -> OrderRead:
    return OrderRead.model_validate(OrderService(session).get_order(order_id, user=current_user))


@router.patch(
    "/{order_id}",
    response_model=OrderRead,
    summary="Редагувати замовлення",
    description="ADMIN і DISPATCHER редагують будь-яке замовлення. CUSTOMER - лише своє "
    "і лише доки воно не скасоване й не передане кур'єру.",
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def update_order(
    payload: OrderUpdate,
    session: DbSession,
    current_user: CurrentUser,
    order_id: Annotated[int, Path(ge=1)],
) -> OrderRead:
    return OrderRead.model_validate(
        OrderService(session).update_order(order_id, payload, user=current_user)
    )


@router.post(
    "/{order_id}/status",
    response_model=OrderRead,
    summary="Змінити статус замовлення",
    description="Доступно ролям ADMIN і DISPATCHER. Неправильні переходи статусів заборонені.",
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Заборонений перехід статусу"},
    },
)
def change_order_status(
    payload: OrderStatusChange,
    session: DbSession,
    current_user: CurrentUser,
    order_id: Annotated[int, Path(ge=1)],
) -> OrderRead:
    return OrderRead.model_validate(
        OrderService(session).change_status(order_id, payload, user=current_user)
    )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderRead,
    summary="Скасувати замовлення",
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def cancel_order(
    session: DbSession,
    current_user: CurrentUser,
    order_id: Annotated[int, Path(ge=1)],
    payload: OrderCancel | None = None,
) -> OrderRead:
    return OrderRead.model_validate(
        OrderService(session).cancel_order(order_id, payload or OrderCancel(), user=current_user)
    )


@router.get(
    "/{order_id}/history",
    response_model=list[OrderStatusHistoryRead],
    summary="Історія статусів замовлення",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_order_history(
    session: DbSession,
    current_user: CurrentUser,
    order_id: Annotated[int, Path(ge=1)],
) -> list[OrderStatusHistoryRead]:
    entries = OrderService(session).get_history(order_id, user=current_user)
    return [OrderStatusHistoryRead.model_validate(entry) for entry in entries]
