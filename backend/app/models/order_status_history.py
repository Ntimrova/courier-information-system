"""Історія змін статусу замовлення."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import OrderStatus
from app.database.base import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.order import Order
    from app.models.user import User


class OrderStatusHistory(Base):
    """Один запис про зміну статусу.

    Працює як журнал у відділенні пошти: кожен рух посилки фіксується
    окремим рядком, і жоден рядок згодом не редагується.
    """

    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    previous_status: Mapped[OrderStatus | None] = mapped_column(
        SAEnum(OrderStatus, name="order_status", native_enum=True, create_type=False),
        nullable=True,
    )
    new_status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status", native_enum=True, create_type=False),
        nullable=False,
    )
    changed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    order: Mapped[Order] = relationship(back_populates="status_history")
    changed_by: Mapped[User | None] = relationship(
        back_populates="status_changes", foreign_keys=[changed_by_user_id]
    )

    __table_args__ = (
        Index("ix_order_status_history_order_id_created_at", "order_id", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<OrderStatusHistory order_id={self.order_id} "
            f"{self.previous_status} -> {self.new_status}>"
        )
