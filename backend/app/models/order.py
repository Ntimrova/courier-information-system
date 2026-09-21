"""Модель замовлення."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DeliveryType, OrderStatus, PackageSize
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.order_status_history import OrderStatusHistory
    from app.models.user import User


class Order(Base, TimestampMixin):
    """Замовлення на доставку."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_number: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Відправник і місце забору
    sender_name: Mapped[str] = mapped_column(String(160), nullable=False)
    sender_phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    pickup_address: Mapped[str] = mapped_column(String(300), nullable=False)

    # Одержувач і місце доставки
    recipient_name: Mapped[str] = mapped_column(String(160), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    delivery_address: Mapped[str] = mapped_column(String(300), nullable=False)

    # Відправлення
    package_description: Mapped[str] = mapped_column(String(500), nullable=False)
    package_weight: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    package_size: Mapped[PackageSize] = mapped_column(
        SAEnum(PackageSize, name="package_size", native_enum=True, validate_strings=True),
        nullable=False,
    )
    delivery_type: Mapped[DeliveryType] = mapped_column(
        SAEnum(DeliveryType, name="delivery_type", native_enum=True, validate_strings=True),
        nullable=False,
        default=DeliveryType.STANDARD,
        index=True,
    )
    desired_delivery_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status", native_enum=True, validate_strings=True),
        nullable=False,
        default=OrderStatus.CREATED,
        index=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped[User] = relationship(back_populates="orders", foreign_keys=[customer_id])
    status_history: Mapped[list[OrderStatusHistory]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderStatusHistory.created_at",
    )

    __table_args__ = (
        CheckConstraint("package_weight > 0", name="package_weight_positive"),
        CheckConstraint(
            "pickup_address <> delivery_address", name="addresses_must_differ"
        ),
        Index("ix_orders_status_created_at", "status", "created_at"),
        Index("ix_orders_customer_id_status", "customer_id", "status"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order id={self.id} tracking={self.tracking_number!r} status={self.status}>"
