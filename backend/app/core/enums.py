"""Перелічення (enum), спільні для всієї системи."""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Ролі користувачів системи."""

    ADMIN = "ADMIN"
    DISPATCHER = "DISPATCHER"
    COURIER = "COURIER"
    CUSTOMER = "CUSTOMER"
    MANAGER = "MANAGER"


class OrderStatus(str, Enum):
    """Статуси замовлення.

    Перші чотири використовуються вже в частині 1.
    Решта зарезервовані для частини 2 (кур'єри та доставка) і поки
    не встановлюються жодною бізнес-операцією.
    """

    # Частина 1
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    WAITING_FOR_COURIER = "WAITING_FOR_COURIER"
    CANCELLED = "CANCELLED"

    # Зарезервовано для частини 2
    COURIER_ASSIGNED = "COURIER_ASSIGNED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    DELIVERY_FAILED = "DELIVERY_FAILED"


class DeliveryType(str, Enum):
    """Тип доставки."""

    STANDARD = "STANDARD"
    EXPRESS = "EXPRESS"


class PackageSize(str, Enum):
    """Розмір відправлення."""

    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


#: Статуси, доступні в першій частині системи.
PART_ONE_STATUSES: frozenset[OrderStatus] = frozenset(
    {
        OrderStatus.CREATED,
        OrderStatus.CONFIRMED,
        OrderStatus.WAITING_FOR_COURIER,
        OrderStatus.CANCELLED,
    }
)

#: Статуси, у яких замовлення вважається активним (не завершене і не скасоване).
ACTIVE_STATUSES: frozenset[OrderStatus] = frozenset(
    {
        OrderStatus.CREATED,
        OrderStatus.CONFIRMED,
        OrderStatus.WAITING_FOR_COURIER,
    }
)

#: Статуси, у яких клієнт ще може редагувати або скасувати своє замовлення.
#: Щойно замовлення передане кур'єру (частина 2), редагування закривається.
CUSTOMER_EDITABLE_STATUSES: frozenset[OrderStatus] = frozenset(
    {
        OrderStatus.CREATED,
        OrderStatus.CONFIRMED,
        OrderStatus.WAITING_FOR_COURIER,
    }
)
