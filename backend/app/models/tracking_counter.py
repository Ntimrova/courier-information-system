"""Лічильник номерів відстеження по роках.

Один рядок на рік. Під час створення замовлення рядок блокується
(`SELECT ... FOR UPDATE`), число збільшується на одиницю - і два паралельні
запити ніколи не отримають однаковий tracking_number.
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class TrackingCounter(Base):
    """Останній використаний порядковий номер замовлення за рік."""

    __tablename__ = "order_tracking_counters"

    year: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    last_number: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TrackingCounter year={self.year} last_number={self.last_number}>"
