"""Схеми dashboard."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.enums import UserRole
from app.schemas.order import OrderListItem


class OrderCounters(BaseModel):
    """Лічильники замовлень за статусами."""

    total: int = Field(ge=0)
    created: int = Field(ge=0)
    confirmed: int = Field(ge=0)
    waiting_for_courier: int = Field(ge=0)
    cancelled: int = Field(ge=0)
    active: int = Field(ge=0, description="CREATED + CONFIRMED + WAITING_FOR_COURIER")


class DashboardSummary(BaseModel):
    """Зведення для головної сторінки. Склад залежить від ролі."""

    role: UserRole
    scope: str = Field(description="all - усі замовлення, own - лише власні")
    counters: OrderCounters
    recent_orders: list[OrderListItem]
    total_users: int | None = Field(
        default=None, description="Заповнюється лише для ADMIN і MANAGER"
    )
    active_users: int | None = None
