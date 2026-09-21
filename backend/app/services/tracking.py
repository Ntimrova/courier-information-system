"""Генерація номера відстеження (tracking number).

Формат: LDC-<рік>-<шість цифр>, наприклад `LDC-2026-000001`.
LDC - Local Delivery Company.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tracking_counter import TrackingCounter

TRACKING_PREFIX = "LDC"
TRACKING_NUMBER_WIDTH = 6


def format_tracking_number(year: int, number: int) -> str:
    """Збирає номер у людському вигляді."""
    return f"{TRACKING_PREFIX}-{year}-{number:0{TRACKING_NUMBER_WIDTH}d}"


def generate_tracking_number(session: Session, *, today: date | None = None) -> str:
    """Видає наступний унікальний номер для поточного року.

    Рядок лічильника блокується на час транзакції, тож два одночасні
    замовлення отримають різні номери.
    """
    year = (today or date.today()).year

    counter = session.execute(
        select(TrackingCounter).where(TrackingCounter.year == year).with_for_update()
    ).scalar_one_or_none()

    if counter is None:
        counter = TrackingCounter(year=year, last_number=0)
        session.add(counter)
        session.flush()
        counter = session.execute(
            select(TrackingCounter).where(TrackingCounter.year == year).with_for_update()
        ).scalar_one()

    counter.last_number += 1
    session.flush()
    return format_tracking_number(year, counter.last_number)
