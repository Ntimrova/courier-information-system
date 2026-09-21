"""Доступ до таблиці історії статусів."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import OrderStatus
from app.models.order_status_history import OrderStatusHistory


class HistoryRepository:
    """Репозиторій історії змін статусу замовлення."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_order(self, order_id: int) -> list[OrderStatusHistory]:
        stmt = (
            select(OrderStatusHistory)
            .where(OrderStatusHistory.order_id == order_id)
            .options(joinedload(OrderStatusHistory.changed_by))
            .order_by(OrderStatusHistory.created_at.asc(), OrderStatusHistory.id.asc())
        )
        return list(self.session.execute(stmt).unique().scalars().all())

    def record(
        self,
        *,
        order_id: int,
        previous_status: OrderStatus | None,
        new_status: OrderStatus,
        changed_by_user_id: int | None,
        comment: str | None = None,
    ) -> OrderStatusHistory:
        """Додає запис в журнал. Викликається на кожну зміну статусу."""
        entry = OrderStatusHistory(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by_user_id=changed_by_user_id,
            comment=comment,
        )
        self.session.add(entry)
        self.session.flush()
        return entry
