"""Зведені показники для головної сторінки."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import OrderStatus, UserRole
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.dashboard import DashboardSummary, OrderCounters
from app.schemas.order import OrderListItem
from app.services.order_service import OrderService

RECENT_ORDERS_LIMIT = 5


class DashboardService:
    """Рахує показники прямо в PostgreSQL, без кешів і заглушок."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.users = UserRepository(session)

    def summary(self, user: User) -> DashboardSummary:
        scope = OrderService.scope_for(user)

        if scope == "none":
            return DashboardSummary(
                role=user.role,
                scope=scope,
                counters=OrderCounters(
                    total=0, created=0, confirmed=0, waiting_for_courier=0, cancelled=0, active=0
                ),
                recent_orders=[],
            )

        customer_id = user.id if scope == "own" else None
        by_status = self.orders.count_by_status(customer_id=customer_id)

        created = by_status.get(OrderStatus.CREATED, 0)
        confirmed = by_status.get(OrderStatus.CONFIRMED, 0)
        waiting = by_status.get(OrderStatus.WAITING_FOR_COURIER, 0)
        cancelled = by_status.get(OrderStatus.CANCELLED, 0)

        counters = OrderCounters(
            total=sum(by_status.values()),
            created=created,
            confirmed=confirmed,
            waiting_for_courier=waiting,
            cancelled=cancelled,
            active=created + confirmed + waiting,
        )

        recent = self.orders.recent_orders(limit=RECENT_ORDERS_LIMIT, customer_id=customer_id)

        summary = DashboardSummary(
            role=user.role,
            scope=scope,
            counters=counters,
            recent_orders=[OrderListItem.model_validate(order) for order in recent],
        )

        if user.role == UserRole.ADMIN:
            summary.total_users = self.users.count_all()
            summary.active_users = self.users.count_active()

        return summary
