"""Доступ до таблиці замовлень."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import ACTIVE_STATUSES, DeliveryType, OrderStatus
from app.core.pagination import Page, PageParams, SortParams
from app.models.order import Order
from app.models.user import User

#: Поля, за якими дозволено сортувати список замовлень.
ORDER_SORT_FIELDS: dict[str, object] = {
    "id": Order.id,
    "tracking_number": Order.tracking_number,
    "status": Order.status,
    "delivery_type": Order.delivery_type,
    "desired_delivery_date": Order.desired_delivery_date,
    "created_at": Order.created_at,
    "updated_at": Order.updated_at,
}


class OrderRepository:
    """Репозиторій замовлень."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- Читання ---

    def get_by_id(self, order_id: int, *, with_customer: bool = True) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        if with_customer:
            stmt = stmt.options(joinedload(Order.customer))
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def get_by_tracking_number(self, tracking_number: str) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.tracking_number == tracking_number)
            .options(joinedload(Order.customer))
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def _apply_filters(
        self,
        stmt: Select,
        *,
        search: str | None,
        status: OrderStatus | None,
        delivery_type: DeliveryType | None,
        date_from: date | None,
        date_to: date | None,
        customer_id: int | None,
    ) -> Select:
        if search:
            pattern = f"%{search.strip().lower()}%"
            stmt = stmt.join(User, User.id == Order.customer_id).where(
                or_(
                    func.lower(Order.tracking_number).like(pattern),
                    func.lower(Order.sender_phone).like(pattern),
                    func.lower(Order.recipient_phone).like(pattern),
                    func.lower(Order.sender_name).like(pattern),
                    func.lower(Order.recipient_name).like(pattern),
                    func.lower(User.first_name).like(pattern),
                    func.lower(User.last_name).like(pattern),
                    func.lower(User.phone).like(pattern),
                )
            )
        if status is not None:
            stmt = stmt.where(Order.status == status)
        if delivery_type is not None:
            stmt = stmt.where(Order.delivery_type == delivery_type)
        if date_from is not None:
            stmt = stmt.where(Order.desired_delivery_date >= date_from)
        if date_to is not None:
            stmt = stmt.where(Order.desired_delivery_date <= date_to)
        if customer_id is not None:
            stmt = stmt.where(Order.customer_id == customer_id)
        return stmt

    def list_orders(
        self,
        *,
        page: PageParams,
        sort: SortParams,
        search: str | None = None,
        status: OrderStatus | None = None,
        delivery_type: DeliveryType | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        customer_id: int | None = None,
    ) -> Page[Order]:
        """Сторінка замовлень із пошуком, фільтрами й сортуванням."""
        filters = {
            "search": search,
            "status": status,
            "delivery_type": delivery_type,
            "date_from": date_from,
            "date_to": date_to,
            "customer_id": customer_id,
        }
        count_stmt = self._apply_filters(
            select(func.count(func.distinct(Order.id))).select_from(Order), **filters
        )
        total = int(self.session.execute(count_stmt).scalar_one())

        column = ORDER_SORT_FIELDS.get(sort.sort_by, Order.created_at)
        order_by = column.desc() if sort.descending else column.asc()  # type: ignore[union-attr]

        stmt = self._apply_filters(select(Order), **filters)
        stmt = (
            stmt.options(joinedload(Order.customer))
            .order_by(order_by, Order.id.desc())
            .offset(page.offset)
            .limit(page.limit)
        )
        items = list(self.session.execute(stmt).unique().scalars().all())
        return Page(items=items, total=total, page=page.page, page_size=page.page_size)

    def recent_orders(self, *, limit: int = 5, customer_id: int | None = None) -> list[Order]:
        """Останні створені замовлення."""
        stmt = select(Order).options(joinedload(Order.customer))
        if customer_id is not None:
            stmt = stmt.where(Order.customer_id == customer_id)
        stmt = stmt.order_by(Order.created_at.desc(), Order.id.desc()).limit(limit)
        return list(self.session.execute(stmt).unique().scalars().all())

    def count_by_status(self, *, customer_id: int | None = None) -> dict[OrderStatus, int]:
        """Кількість замовлень у розрізі статусів - один запит замість п'яти."""
        stmt = select(Order.status, func.count()).group_by(Order.status)
        if customer_id is not None:
            stmt = stmt.where(Order.customer_id == customer_id)
        rows = self.session.execute(stmt).all()
        return {OrderStatus(row[0]): int(row[1]) for row in rows}

    def count_active(self, *, customer_id: int | None = None) -> int:
        stmt = (
            select(func.count())
            .select_from(Order)
            .where(Order.status.in_(list(ACTIVE_STATUSES)))
        )
        if customer_id is not None:
            stmt = stmt.where(Order.customer_id == customer_id)
        return int(self.session.execute(stmt).scalar_one())

    # --- Запис ---

    def add(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        return order

    def commit(self) -> None:
        self.session.commit()
