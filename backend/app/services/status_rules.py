"""Правила переходів між статусами замовлення.

Усе зібрано в одному словнику. Щоб у частині 2 додати кур'єрські статуси,
достатньо дописати рядки сюди, а не шукати перевірки по всьому коду.

Аналогія: це схема ліній метро. Потяг може поїхати лише туди, куди веде
колія, а не в будь-яку станцію на карті.
"""

from __future__ import annotations

from app.core.enums import ACTIVE_STATUSES, OrderStatus, UserRole
from app.core.errors import InvalidStatusTransitionError, PermissionDeniedError

#: Дозволені переходи першої частини.
ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.CREATED: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset(
        {OrderStatus.WAITING_FOR_COURIER, OrderStatus.CANCELLED}
    ),
    OrderStatus.WAITING_FOR_COURIER: frozenset({OrderStatus.CANCELLED}),
    OrderStatus.CANCELLED: frozenset(),
}

#: Хто має право змінювати статус вручну.
STATUS_CHANGE_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN, UserRole.DISPATCHER})

#: Хто має право скасовувати замовлення (клієнт - лише своє).
CANCEL_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.ADMIN, UserRole.DISPATCHER, UserRole.CUSTOMER}
)

#: Людські назви статусів для повідомлень про помилки.
STATUS_LABELS: dict[OrderStatus, str] = {
    OrderStatus.CREATED: "Створено",
    OrderStatus.CONFIRMED: "Підтверджено",
    OrderStatus.WAITING_FOR_COURIER: "Очікує кур'єра",
    OrderStatus.CANCELLED: "Скасовано",
    OrderStatus.COURIER_ASSIGNED: "Призначено кур'єра",
    OrderStatus.PICKED_UP: "Забрано",
    OrderStatus.IN_TRANSIT: "У дорозі",
    OrderStatus.DELIVERED: "Доставлено",
    OrderStatus.DELIVERY_FAILED: "Доставка не вдалася",
}


def status_label(status: OrderStatus) -> str:
    return STATUS_LABELS.get(status, status.value)


def allowed_next_statuses(current: OrderStatus) -> frozenset[OrderStatus]:
    """Куди можна перейти з поточного статусу."""
    return ALLOWED_TRANSITIONS.get(current, frozenset())


def is_transition_allowed(current: OrderStatus, target: OrderStatus) -> bool:
    return target in allowed_next_statuses(current)


def ensure_transition_allowed(current: OrderStatus, target: OrderStatus) -> None:
    """Кидає помилку, якщо перехід заборонено."""
    if current == target:
        raise InvalidStatusTransitionError(
            f"Замовлення вже має статус «{status_label(current)}»"
        )
    if not is_transition_allowed(current, target):
        allowed = allowed_next_statuses(current)
        if allowed:
            options = ", ".join(
                f"«{status_label(item)}»" for item in sorted(allowed, key=lambda s: s.value)
            )
            hint = f" Доступні статуси: {options}."
        else:
            hint = " Замовлення вже в кінцевому статусі."
        raise InvalidStatusTransitionError(
            f"Перехід «{status_label(current)}» -> «{status_label(target)}» заборонено.{hint}"
        )


def ensure_role_can_change_status(role: UserRole) -> None:
    """Змінювати статус вручну можуть лише адміністратор і диспетчер."""
    if role not in STATUS_CHANGE_ROLES:
        raise PermissionDeniedError("Змінювати статус замовлення можуть адміністратор і диспетчер")


def is_cancellable(status: OrderStatus) -> bool:
    """Замовлення можна скасувати, доки воно активне."""
    return status in ACTIVE_STATUSES
