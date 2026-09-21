"""Наповнення бази тестовими даними.

Запуск (з каталогу backend):

    python -m scripts.seed

Скрипт ідемпотентний: повторний запуск не створює дублікатів.
Паролі беруться зі змінної SEED_DEFAULT_PASSWORD і призначені лише для
локальної демонстрації.
"""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Дозволяє запускати скрипт напряму: python scripts/seed.py
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.enums import (  # noqa: E402
    DeliveryType,
    OrderStatus,
    PackageSize,
    UserRole,
)
from app.core.security import hash_password  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models.order import Order  # noqa: E402
from app.models.order_status_history import OrderStatusHistory  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.tracking import generate_tracking_number  # noqa: E402

DEFAULT_PASSWORD = settings.seed_default_password

#: Тестові облікові записи. Ті самі дані описані в README.
SEED_USERS: list[dict[str, object]] = [
    {
        "first_name": "Оксана",
        "last_name": "Адміненко",
        "email": settings.seed_admin_email,
        "phone": "+380671000001",
        "role": UserRole.ADMIN,
    },
    {
        "first_name": "Дмитро",
        "last_name": "Диспетченко",
        "email": "dispatcher@courier.ua",
        "phone": "+380671000002",
        "role": UserRole.DISPATCHER,
    },
    {
        "first_name": "Ігор",
        "last_name": "Кур'єренко",
        "email": "courier@courier.ua",
        "phone": "+380671000004",
        "role": UserRole.COURIER,
    },
    {
        "first_name": "Олена",
        "last_name": "Клієнтенко",
        "email": "customer1@courier.ua",
        "phone": "+380671000005",
        "role": UserRole.CUSTOMER,
    },
    {
        "first_name": "Павло",
        "last_name": "Замовленко",
        "email": "customer2@courier.ua",
        "phone": "+380671000006",
        "role": UserRole.CUSTOMER,
    },
]


def _get_or_create_user(session: Session, data: dict[str, object]) -> User:
    email = str(data["email"]).lower()
    existing = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing is not None:
        return existing

    user = User(
        first_name=str(data["first_name"]),
        last_name=str(data["last_name"]),
        email=email,
        phone=str(data["phone"]),
        password_hash=hash_password(DEFAULT_PASSWORD),
        role=data["role"],  # type: ignore[arg-type]
        is_active=True,
    )
    session.add(user)
    session.flush()
    return user


def _create_order(
    session: Session,
    *,
    customer: User,
    author: User,
    sender_name: str,
    sender_phone: str,
    pickup_address: str,
    recipient_name: str,
    recipient_phone: str,
    delivery_address: str,
    package_description: str,
    package_weight: Decimal,
    package_size: PackageSize,
    delivery_type: DeliveryType,
    days_ahead: int,
    comment: str | None,
    transitions: list[tuple[OrderStatus, str]],
) -> Order:
    """Створює замовлення і проводить його через ланцюжок статусів."""
    order = Order(
        tracking_number=generate_tracking_number(session),
        customer_id=customer.id,
        sender_name=sender_name,
        sender_phone=sender_phone,
        pickup_address=pickup_address,
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        delivery_address=delivery_address,
        package_description=package_description,
        package_weight=package_weight,
        package_size=package_size,
        delivery_type=delivery_type,
        desired_delivery_date=date.today() + timedelta(days=days_ahead),
        comment=comment,
        status=OrderStatus.CREATED,
    )
    session.add(order)
    session.flush()

    session.add(
        OrderStatusHistory(
            order_id=order.id,
            previous_status=None,
            new_status=OrderStatus.CREATED,
            changed_by_user_id=customer.id,
            comment="Замовлення створено",
        )
    )

    current = OrderStatus.CREATED
    for target_status, note in transitions:
        session.add(
            OrderStatusHistory(
                order_id=order.id,
                previous_status=current,
                new_status=target_status,
                changed_by_user_id=author.id,
                comment=note,
            )
        )
        current = target_status
        order.status = target_status
        if target_status == OrderStatus.CANCELLED:
            order.cancelled_at = datetime.now(UTC)

    session.flush()
    return order


def seed() -> None:
    """Створює користувачів і демонстраційні замовлення."""
    session: Session = SessionLocal()
    try:
        users = {str(data["email"]): _get_or_create_user(session, data) for data in SEED_USERS}
        session.commit()

        admin = users[settings.seed_admin_email.lower()]
        dispatcher = users["dispatcher@courier.ua"]
        customer_one = users["customer1@courier.ua"]
        customer_two = users["customer2@courier.ua"]

        existing_orders = session.execute(select(Order.id)).first()
        if existing_orders is not None:
            print("Замовлення вже є в базі - пропускаю створення демонстраційних замовлень.")
            _print_credentials()
            return

        _create_order(
            session,
            customer=customer_one,
            author=customer_one,
            sender_name="Олена Клієнтенко",
            sender_phone="+380671000005",
            pickup_address="м. Київ, вул. Хрещатик, 22, кв. 14",
            recipient_name="Андрій Бондар",
            recipient_phone="+380931112233",
            delivery_address="м. Київ, вул. Січових Стрільців, 7, офіс 4",
            package_description="Документи в конверті A4",
            package_weight=Decimal("0.300"),
            package_size=PackageSize.SMALL,
            delivery_type=DeliveryType.EXPRESS,
            days_ahead=1,
            comment="Зателефонувати за 15 хвилин до приїзду",
            transitions=[],
        )

        _create_order(
            session,
            customer=customer_one,
            author=dispatcher,
            sender_name="Олена Клієнтенко",
            sender_phone="+380671000005",
            pickup_address="м. Київ, вул. Хрещатик, 22, кв. 14",
            recipient_name="Світлана Гриценко",
            recipient_phone="+380951234567",
            delivery_address="м. Київ, пр. Науки, 12, під'їзд 2",
            package_description="Коробка з книгами",
            package_weight=Decimal("4.500"),
            package_size=PackageSize.MEDIUM,
            delivery_type=DeliveryType.STANDARD,
            days_ahead=2,
            comment=None,
            transitions=[(OrderStatus.CONFIRMED, "Замовлення підтверджено диспетчером")],
        )

        _create_order(
            session,
            customer=customer_two,
            author=dispatcher,
            sender_name="Павло Замовленко",
            sender_phone="+380671000006",
            pickup_address="м. Львів, вул. Городоцька, 100",
            recipient_name="Тарас Левко",
            recipient_phone="+380677654321",
            delivery_address="м. Львів, вул. Зелена, 45, кв. 9",
            package_description="Запчастини для велосипеда",
            package_weight=Decimal("7.250"),
            package_size=PackageSize.LARGE,
            delivery_type=DeliveryType.STANDARD,
            days_ahead=3,
            comment="Крихке, не кидати",
            transitions=[
                (OrderStatus.CONFIRMED, "Замовлення підтверджено"),
                (OrderStatus.WAITING_FOR_COURIER, "Передано в очікування кур'єра"),
            ],
        )

        _create_order(
            session,
            customer=customer_two,
            author=admin,
            sender_name="Павло Замовленко",
            sender_phone="+380671000006",
            pickup_address="м. Львів, вул. Городоцька, 100",
            recipient_name="Ірина Мельник",
            recipient_phone="+380632223344",
            delivery_address="м. Львів, вул. Стрийська, 30, офіс 12",
            package_description="Подарунковий набір",
            package_weight=Decimal("1.100"),
            package_size=PackageSize.SMALL,
            delivery_type=DeliveryType.EXPRESS,
            days_ahead=1,
            comment=None,
            transitions=[(OrderStatus.CANCELLED, "Клієнт передумав")],
        )

        _create_order(
            session,
            customer=customer_one,
            author=customer_one,
            sender_name="Олена Клієнтенко",
            sender_phone="+380671000005",
            pickup_address="м. Київ, вул. Хрещатик, 22, кв. 14",
            recipient_name="Віктор Савчук",
            recipient_phone="+380504445566",
            delivery_address="м. Київ, вул. Антоновича, 3, кв. 88",
            package_description="Ноутбук у захисному кейсі",
            package_weight=Decimal("2.800"),
            package_size=PackageSize.MEDIUM,
            delivery_type=DeliveryType.EXPRESS,
            days_ahead=4,
            comment="Тільки особисто в руки одержувачу",
            transitions=[],
        )

        session.commit()
        print("Тестові дані створено.")
        _print_credentials()
    finally:
        session.close()


def _print_credentials() -> None:
    print("\nТестові облікові записи (пароль для всіх однаковий):")
    for data in SEED_USERS:
        print(f"  {str(data['role'].value):<11} {data['email']:<26} {DEFAULT_PASSWORD}")  # type: ignore[union-attr]


if __name__ == "__main__":
    seed()
