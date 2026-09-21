"""Тести реєстрації, входу й доступу до власних даних."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.tests.conftest import DEFAULT_PASSWORD, auth_headers, create_user


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_register_creates_customer_and_returns_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Нова",
            "last_name": "Клієнтка",
            "email": "new.customer@test.ua",
            "phone": "+380671112233",
            "password": DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["role"] == UserRole.CUSTOMER.value
    assert body["user"]["is_active"] is True
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_normalizes_phone(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Оля",
            "last_name": "Пробна",
            "email": "phone.format@test.ua",
            "phone": "+38 (067) 111-22-44",
            "password": DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["user"]["phone"] == "+380671112244"


def test_register_rejects_duplicate_email(client: TestClient, customer) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Дубль",
            "last_name": "Клієнт",
            "email": customer.email,
            "phone": "+380671112255",
            "password": DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_USED"


def test_register_rejects_invalid_phone(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Погана",
            "last_name": "Адреса",
            "email": "bad.phone@test.ua",
            "phone": "123",
            "password": DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_success(client: TestClient, customer) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": customer.email, "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 200, response.text
    assert response.json()["user"]["email"] == customer.email


def test_login_with_wrong_password_is_rejected(client: TestClient, customer) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": customer.email, "password": "WrongPassword123!"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "INVALID_CREDENTIALS"
    assert body["error"]["message"] == "Неправильний email або пароль"


def test_login_with_unknown_email_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@test.ua", "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_inactive_user_cannot_log_in(client: TestClient, db_session: Session) -> None:
    blocked = create_user(
        db_session,
        email="blocked@test.ua",
        role=UserRole.CUSTOMER,
        is_active=False,
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": blocked.email, "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "USER_INACTIVE"


def test_blocked_after_login_loses_access(
    client: TestClient, db_session: Session, customer, admin
) -> None:
    """Токен, виданий до блокування, більше не працює."""
    headers = auth_headers(client, customer.email)
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    admin_headers = auth_headers(client, admin.email)
    response = client.patch(
        f"/api/v1/users/{customer.id}/status",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert response.status_code == 200

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "USER_INACTIVE"


def test_me_returns_current_user(client: TestClient, customer) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_headers(client, customer.email))
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == customer.email
    assert body["full_name"] == f"{customer.first_name} {customer.last_name}"


def test_me_without_token_is_unauthorized(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_me_with_broken_token_is_unauthorized(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"


def test_logout_returns_message(client: TestClient, customer) -> None:
    response = client.post("/api/v1/auth/logout", headers=auth_headers(client, customer.email))
    assert response.status_code == 200
    assert response.json()["message"]


def test_password_is_never_stored_in_plain_text(client: TestClient, db_session: Session) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Секретна",
            "last_name": "Особа",
            "email": "secret@test.ua",
            "phone": "+380671119988",
            "password": DEFAULT_PASSWORD,
        },
    )
    from sqlalchemy import select

    from app.models.user import User

    stored = db_session.execute(
        select(User).where(User.email == "secret@test.ua")
    ).scalar_one()
    assert stored.password_hash != DEFAULT_PASSWORD
    assert stored.password_hash.startswith("$2b$")
