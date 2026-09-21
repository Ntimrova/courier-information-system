"""Схеми замовлень і історії статусів."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import DeliveryType, OrderStatus, PackageSize
from app.schemas.common import Phone, TrimmedStr
from app.schemas.user import UserShort

MAX_PACKAGE_WEIGHT_KG = Decimal("1000")


def _addresses_differ(pickup: str | None, delivery: str | None) -> None:
    """Адреси забору й доставки не можуть збігатися."""
    if pickup is None or delivery is None:
        return
    if pickup.strip().casefold() == delivery.strip().casefold():
        raise ValueError("Адреса отримання та адреса доставки не повинні збігатися")


class OrderBase(BaseModel):
    sender_name: TrimmedStr = Field(min_length=2, max_length=160, examples=["Іван Петренко"])
    sender_phone: Phone = Field(examples=["+380671234567"])
    pickup_address: TrimmedStr = Field(
        min_length=5, max_length=300, examples=["м. Київ, вул. Хрещатик, 1, кв. 5"]
    )
    recipient_name: TrimmedStr = Field(min_length=2, max_length=160, examples=["Марія Шевченко"])
    recipient_phone: Phone = Field(examples=["+380501112233"])
    delivery_address: TrimmedStr = Field(
        min_length=5, max_length=300, examples=["м. Київ, пр. Науки, 12, офіс 3"]
    )
    package_description: TrimmedStr = Field(
        min_length=3, max_length=500, examples=["Документи в конверті A4"]
    )
    package_weight: Decimal = Field(
        gt=Decimal("0"),
        le=MAX_PACKAGE_WEIGHT_KG,
        max_digits=7,
        decimal_places=3,
        description="Вага в кілограмах, більша за нуль",
        examples=[Decimal("1.500")],
    )
    package_size: PackageSize = Field(examples=[PackageSize.SMALL])
    delivery_type: DeliveryType = Field(default=DeliveryType.STANDARD)
    desired_delivery_date: date = Field(examples=["2026-10-01"])
    comment: TrimmedStr | None = Field(default=None, max_length=1000)


class OrderCreate(OrderBase):
    """Створення замовлення.

    `customer_id` вказує лише диспетчер чи адміністратор, коли оформлює
    замовлення від імені клієнта. Клієнт це поле не надсилає.
    """

    customer_id: int | None = Field(
        default=None,
        description="Клієнт, від імені якого створюється замовлення (ADMIN/DISPATCHER)",
    )

    @model_validator(mode="after")
    def _check(self) -> OrderCreate:
        _addresses_differ(self.pickup_address, self.delivery_address)
        if self.desired_delivery_date < date.today():
            raise ValueError("Бажана дата доставки не може бути в минулому")
        return self


class OrderUpdate(BaseModel):
    """Часткове редагування замовлення."""

    sender_name: TrimmedStr | None = Field(default=None, min_length=2, max_length=160)
    sender_phone: Phone | None = None
    pickup_address: TrimmedStr | None = Field(default=None, min_length=5, max_length=300)
    recipient_name: TrimmedStr | None = Field(default=None, min_length=2, max_length=160)
    recipient_phone: Phone | None = None
    delivery_address: TrimmedStr | None = Field(default=None, min_length=5, max_length=300)
    package_description: TrimmedStr | None = Field(default=None, min_length=3, max_length=500)
    package_weight: Decimal | None = Field(
        default=None,
        gt=Decimal("0"),
        le=MAX_PACKAGE_WEIGHT_KG,
        max_digits=7,
        decimal_places=3,
    )
    package_size: PackageSize | None = None
    delivery_type: DeliveryType | None = None
    desired_delivery_date: date | None = None
    comment: TrimmedStr | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def _check(self) -> OrderUpdate:
        _addresses_differ(self.pickup_address, self.delivery_address)
        if self.desired_delivery_date is not None and self.desired_delivery_date < date.today():
            raise ValueError("Бажана дата доставки не може бути в минулому")
        return self

    def changes(self) -> dict[str, object]:
        """Лише ті поля, які клієнт справді надіслав."""
        return self.model_dump(exclude_unset=True)


class OrderStatusChange(BaseModel):
    """Запит на зміну статусу."""

    status: OrderStatus
    comment: TrimmedStr | None = Field(default=None, max_length=500)


class OrderCancel(BaseModel):
    """Скасування замовлення з необов'язковою причиною."""

    comment: TrimmedStr | None = Field(default=None, max_length=500)


class OrderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    previous_status: OrderStatus | None
    new_status: OrderStatus
    changed_by_user_id: int | None
    changed_by: UserShort | None = None
    comment: str | None
    created_at: datetime


class OrderRead(BaseModel):
    """Повне представлення замовлення."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tracking_number: str
    customer_id: int
    customer: UserShort | None = None
    sender_name: str
    sender_phone: str
    pickup_address: str
    recipient_name: str
    recipient_phone: str
    delivery_address: str
    package_description: str
    package_weight: Decimal
    package_size: PackageSize
    delivery_type: DeliveryType
    desired_delivery_date: date
    comment: str | None
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None


class OrderListItem(BaseModel):
    """Рядок таблиці замовлень - лише те, що показується в списку."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tracking_number: str
    customer_id: int
    customer: UserShort | None = None
    pickup_address: str
    delivery_address: str
    delivery_type: DeliveryType
    desired_delivery_date: date
    status: OrderStatus
    created_at: datetime
