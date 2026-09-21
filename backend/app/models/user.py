"""Модель користувача."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import UserRole
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.order import Order
    from app.models.order_status_history import OrderStatusHistory


class User(Base, TimestampMixin):
    """Обліковий запис користувача будь-якої ролі."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", native_enum=True, validate_strings=True),
        nullable=False,
        default=UserRole.CUSTOMER,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true", index=True
    )

    orders: Mapped[list[Order]] = relationship(
        back_populates="customer",
        foreign_keys="Order.customer_id",
        cascade="save-update, merge",
    )
    status_changes: Mapped[list[OrderStatusHistory]] = relationship(
        back_populates="changed_by",
        foreign_keys="OrderStatusHistory.changed_by_user_id",
    )

    __table_args__ = (
        Index("ix_users_last_name_first_name", "last_name", "first_name"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
