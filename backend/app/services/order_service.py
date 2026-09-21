"""Бізнес-логіка замовлень: створення, доступ, редагування, статуси."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.core.enums import (
    CUSTOMER_EDITABLE_STATUSES,
    DeliveryType,
    OrderStatus,
    UserRole,
)
from app.core.errors import (
    BusinessRuleError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.core.pagination import Page, PageParams, SortParams
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.user import User
from app.repositories.history_repository import HistoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.order import OrderCancel, OrderCreate, OrderStatusChange, OrderUpdate
from app.services import status_rules
from app.services.tracking import generate_tracking_number

#: Ролі, що бачать усі замовлення.
ORDER_READ_ALL_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN, UserRole.DISPATCHER})

#: Ролі, що можуть створювати й редагувати замовлення.
ORDER_WRITE_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.ADMIN, UserRole.DISPATCHER, UserRole.CUSTOMER}
)

#: Ролі, що можуть створювати замовлення від імені іншого клієнта.
ORDER_CREATE_FOR_OTHERS_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.ADMIN, UserRole.DISPATCHER}
)


class OrderService:
    """Операції над замовленнями з перевіркою прав на backend."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.users = UserRepository(session)
        self.history = HistoryRepository(session)

    # ------------------------------------------------------------------
    # Права доступу
    # ------------------------------------------------------------------

    @staticmethod
    def scope_for(user: User) -> str:
        """Який обсяг замовлень бачить роль: all, own або none."""
        if user.role in ORDER_READ_ALL_ROLES:
            return "all"
        if user.role == UserRole.CUSTOMER:
            return "own"
        # COURIER: у частині 1 доставка ще не реалізована.
        return "none"

    @staticmethod
    def _ensure_can_read(order: Order, user: User) -> None:
        if user.role in ORDER_READ_ALL_ROLES:
            return
        if user.role == UserRole.CUSTOMER and order.customer_id == user.id:
            return
        if user.role == UserRole.COURIER:
            raise PermissionDeniedError(
                "Доступ кур'єра до замовлень з'явиться в наступній частині системи"
            )
        raise PermissionDeniedError("Ви можете переглядати лише власні замовлення")

    @staticmethod
    def _ensure_can_modify(order: Order, user: User) -> None:
        """Перевіряє право редагувати або скасовувати конкретне замовлення."""
        if user.role in {UserRole.ADMIN, UserRole.DISPATCHER}:
            return
        if user.role != UserRole.CUSTOMER or order.customer_id != user.id:
            raise PermissionDeniedError("Ви можете змінювати лише власні замовлення")
        if order.status not in CUSTOMER_EDITABLE_STATUSES:
            raise BusinessRuleError(
                "Замовлення вже не можна змінити: воно скасоване або передане кур'єру"
            )

    # ------------------------------------------------------------------
    # Читання
    # ------------------------------------------------------------------

    def list_orders(
        self,
        *,
        user: User,
        page: PageParams,
        sort: SortParams,
        search: str | None = None,
        status: OrderStatus | None = None,
        delivery_type: DeliveryType | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        customer_id: int | None = None,
    ) -> Page[Order]:
        scope = self.scope_for(user)
        if scope == "none":
            return Page(items=[], total=0, page=page.page, page_size=page.page_size)
        if scope == "own":
            # Клієнт завжди бачить лише свої замовлення, хай там що в query.
            customer_id = user.id

        return self.orders.list_orders(
            page=page,
            sort=sort,
            search=search,
            status=status,
            delivery_type=delivery_type,
            date_from=date_from,
            date_to=date_to,
            customer_id=customer_id,
        )

    def get_order(self, order_id: int, *, user: User) -> Order:
        order = self.orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Замовлення не знайдено", code="ORDER_NOT_FOUND")
        self._ensure_can_read(order, user)
        return order

    def get_history(self, order_id: int, *, user: User) -> list[OrderStatusHistory]:
        order = self.get_order(order_id, user=user)
        return self.history.list_for_order(order.id)

    # ------------------------------------------------------------------
    # Запис
    # ------------------------------------------------------------------

    def create_order(self, payload: OrderCreate, *, user: User) -> Order:
        if user.role not in ORDER_WRITE_ROLES:
            raise PermissionDeniedError("Ця роль не може створювати замовлення")

        customer_id = self._resolve_customer_id(payload.customer_id, user)

        order = Order(
            tracking_number=generate_tracking_number(self.session),
            customer_id=customer_id,
            sender_name=payload.sender_name,
            sender_phone=payload.sender_phone,
            pickup_address=payload.pickup_address,
            recipient_name=payload.recipient_name,
            recipient_phone=payload.recipient_phone,
            delivery_address=payload.delivery_address,
            package_description=payload.package_description,
            package_weight=payload.package_weight,
            package_size=payload.package_size,
            delivery_type=payload.delivery_type,
            desired_delivery_date=payload.desired_delivery_date,
            comment=payload.comment,
            status=OrderStatus.CREATED,
        )
        self.orders.add(order)

        # Перший запис в історії: замовлення з'явилося в системі.
        self.history.record(
            order_id=order.id,
            previous_status=None,
            new_status=OrderStatus.CREATED,
            changed_by_user_id=user.id,
            comment="Замовлення створено",
        )
        self.orders.commit()
        self.session.refresh(order)
        return self.orders.get_by_id(order.id)  # type: ignore[return-value]

    def _resolve_customer_id(self, requested_customer_id: int | None, user: User) -> int:
        """Визначає, кому належатиме замовлення."""
        if user.role == UserRole.CUSTOMER:
            return user.id

        if requested_customer_id is None:
            raise ValidationError(
                "Вкажіть клієнта, від імені якого створюється замовлення",
                details=[{"field": "customer_id", "message": "Обов'язкове поле"}],
            )
        if user.role not in ORDER_CREATE_FOR_OTHERS_ROLES:
            raise PermissionDeniedError("Ця роль не може створювати замовлення для клієнтів")

        customer = self.users.get_by_id(requested_customer_id)
        if customer is None:
            raise NotFoundError("Клієнта не знайдено", code="CUSTOMER_NOT_FOUND")
        if customer.role != UserRole.CUSTOMER:
            raise ValidationError("Замовлення можна створити лише для користувача з роллю CUSTOMER")
        if not customer.is_active:
            raise BusinessRuleError("Обліковий запис клієнта заблоковано")
        return customer.id

    def update_order(self, order_id: int, payload: OrderUpdate, *, user: User) -> Order:
        order = self.orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Замовлення не знайдено", code="ORDER_NOT_FOUND")
        self._ensure_can_modify(order, user)

        if order.status == OrderStatus.CANCELLED:
            raise BusinessRuleError("Скасоване замовлення не можна редагувати")

        changes = payload.changes()
        if not changes:
            return order

        for field, value in changes.items():
            if value is not None or field == "comment":
                setattr(order, field, value)

        # Адреси перевіряємо ще раз: у PATCH могла прийти лише одна з них.
        if order.pickup_address.strip().casefold() == order.delivery_address.strip().casefold():
            raise ValidationError("Адреса отримання та адреса доставки не повинні збігатися")

        self.orders.commit()
        self.session.refresh(order)
        return self.orders.get_by_id(order.id)  # type: ignore[return-value]

    def change_status(
        self, order_id: int, payload: OrderStatusChange, *, user: User
    ) -> Order:
        """Ручна зміна статусу диспетчером або адміністратором."""
        order = self.orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Замовлення не знайдено", code="ORDER_NOT_FOUND")

        status_rules.ensure_role_can_change_status(user.role)
        status_rules.ensure_transition_allowed(order.status, payload.status)

        return self._apply_status(order, payload.status, user=user, comment=payload.comment)

    def cancel_order(self, order_id: int, payload: OrderCancel, *, user: User) -> Order:
        """Скасування замовлення."""
        order = self.orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Замовлення не знайдено", code="ORDER_NOT_FOUND")
        self._ensure_can_modify(order, user)

        if order.status == OrderStatus.CANCELLED:
            raise BusinessRuleError("Замовлення вже скасоване")
        if not status_rules.is_cancellable(order.status):
            raise BusinessRuleError("Це замовлення вже не можна скасувати")

        status_rules.ensure_transition_allowed(order.status, OrderStatus.CANCELLED)
        return self._apply_status(
            order,
            OrderStatus.CANCELLED,
            user=user,
            comment=payload.comment or "Замовлення скасовано",
        )

    def _apply_status(
        self,
        order: Order,
        new_status: OrderStatus,
        *,
        user: User,
        comment: str | None,
    ) -> Order:
        """Змінює статус і завжди пише запис в історію."""
        previous_status = order.status
        order.status = new_status
        if new_status == OrderStatus.CANCELLED:
            order.cancelled_at = datetime.now(UTC)

        self.history.record(
            order_id=order.id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by_user_id=user.id,
            comment=comment,
        )
        self.orders.commit()
        self.session.refresh(order)
        return self.orders.get_by_id(order.id)  # type: ignore[return-value]
