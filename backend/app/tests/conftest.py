"""Спільні фікстури тестів.

Тести працюють проти справжнього PostgreSQL, а не проти заглушки: схема
ставиться тими самими Alembic-міграціями, що й у продакшні. Так помилка в
міграції знайдеться тестом, а не вже на сервері.

Адреса тестової бази береться зі змінної `TEST_DATABASE_URL`.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from datetime import date, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://courier:courier@localhost:5432/courier_test",
)
# Налаштування читаються під час імпорту застосунку, тож підміняємо змінні
# середовища до першого імпорту `app.*`.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")

from alembic.config import Config as AlembicConfig  # noqa: E402

from alembic import command  # noqa: E402
from app.api.deps import get_db  # noqa: E402
from app.core.enums import UserRole  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_PASSWORD = "Password123!"

#: Таблиці, які очищуються перед кожним тестом.
TABLES_TO_CLEAN = (
    "order_status_history",
    "orders",
    "order_tracking_counters",
    "users",
)


@pytest.fixture(scope="session")
def engine():  # type: ignore[no-untyped-def]
    """Двигун тестової бази з накатаними міграціями."""
    test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)

    config = AlembicConfig(os.path.join(BACKEND_ROOT, "alembic.ini"))
    config.set_main_option("script_location", os.path.join(BACKEND_ROOT, "alembic"))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.downgrade(config, "base")
    command.upgrade(config, "head")

    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:  # type: ignore[no-untyped-def]
    """Чиста база для кожного тесту."""
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE " + ", ".join(TABLES_TO_CLEAN) + " RESTART IDENTITY CASCADE")
        )

    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """HTTP-клієнт застосунку, підключений до тестової сесії."""

    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Допоміжні фабрики
# ---------------------------------------------------------------------------


def create_user(
    session: Session,
    *,
    email: str,
    role: UserRole,
    password: str = DEFAULT_PASSWORD,
    is_active: bool = True,
    first_name: str = "Тест",
    last_name: str = "Користувач",
    phone: str = "+380670000000",
) -> User:
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email.lower(),
        phone=phone,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture()
def admin(db_session: Session) -> User:
    return create_user(
        db_session,
        email="admin@test.ua",
        role=UserRole.ADMIN,
        first_name="Оксана",
        last_name="Адміненко",
        phone="+380670000001",
    )


@pytest.fixture()
def dispatcher(db_session: Session) -> User:
    return create_user(
        db_session,
        email="dispatcher@test.ua",
        role=UserRole.DISPATCHER,
        first_name="Дмитро",
        last_name="Диспетченко",
        phone="+380670000002",
    )


@pytest.fixture()
def manager(db_session: Session) -> User:
    return create_user(
        db_session,
        email="manager@test.ua",
        role=UserRole.MANAGER,
        first_name="Марина",
        last_name="Менеджеренко",
        phone="+380670000003",
    )


@pytest.fixture()
def courier(db_session: Session) -> User:
    return create_user(
        db_session,
        email="courier@test.ua",
        role=UserRole.COURIER,
        first_name="Ігор",
        last_name="Кур'єренко",
        phone="+380670000004",
    )


@pytest.fixture()
def customer(db_session: Session) -> User:
    return create_user(
        db_session,
        email="customer@test.ua",
        role=UserRole.CUSTOMER,
        first_name="Олена",
        last_name="Клієнтенко",
        phone="+380670000005",
    )


@pytest.fixture()
def other_customer(db_session: Session) -> User:
    return create_user(
        db_session,
        email="other@test.ua",
        role=UserRole.CUSTOMER,
        first_name="Павло",
        last_name="Замовленко",
        phone="+380670000006",
    )


# ---------------------------------------------------------------------------
# Допоміжні функції для тестів
# ---------------------------------------------------------------------------


def login(client: TestClient, email: str, password: str = DEFAULT_PASSWORD) -> str:
    """Повертає access token."""
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(
    client: TestClient, email: str, password: str = DEFAULT_PASSWORD
) -> dict[str, str]:
    return {"Authorization": f"Bearer {login(client, email, password)}"}


def order_payload(**overrides: Any) -> dict[str, Any]:
    """Коректні дані замовлення; окремі поля можна перевизначити."""
    payload: dict[str, Any] = {
        "sender_name": "Олена Клієнтенко",
        "sender_phone": "+380671234567",
        "pickup_address": "м. Київ, вул. Хрещатик, 22, кв. 14",
        "recipient_name": "Андрій Бондар",
        "recipient_phone": "+380931112233",
        "delivery_address": "м. Київ, вул. Січових Стрільців, 7, офіс 4",
        "package_description": "Документи в конверті A4",
        "package_weight": "1.500",
        "package_size": "SMALL",
        "delivery_type": "STANDARD",
        "desired_delivery_date": (date.today() + timedelta(days=2)).isoformat(),
        "comment": "Зателефонувати заздалегідь",
    }
    payload.update(overrides)
    return payload
