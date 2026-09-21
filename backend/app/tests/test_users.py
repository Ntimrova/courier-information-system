"""Тести управління користувачами та перевірки ролей."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.tests.conftest import DEFAULT_PASSWORD, auth_headers, create_user


def test_admin_can_list_users(client: TestClient, admin, customer, dispatcher) -> None:
    response = client.get("/api/v1/users", headers=auth_headers(client, admin.email))
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == 3
    assert len(body["items"]) == 3


def test_customer_cannot_list_users(client: TestClient, customer) -> None:
    response = client.get("/api/v1/users", headers=auth_headers(client, customer.email))
    assert response.status_code == 403


def test_dispatcher_cannot_list_users(client: TestClient, dispatcher) -> None:
    response = client.get("/api/v1/users", headers=auth_headers(client, dispatcher.email))
    assert response.status_code == 403


def test_admin_creates_user(client: TestClient, admin) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "first_name": "Новий",
            "last_name": "Диспетчер",
            "email": "new.dispatcher@test.ua",
            "phone": "+380671230001",
            "password": DEFAULT_PASSWORD,
            "role": "DISPATCHER",
        },
        headers=auth_headers(client, admin.email),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["role"] == "DISPATCHER"
    assert body["is_active"] is True


def test_admin_updates_user(client: TestClient, admin, customer) -> None:
    response = client.patch(
        f"/api/v1/users/{customer.id}",
        json={"first_name": "Оновлена", "phone": "+380509998877"},
        headers=auth_headers(client, admin.email),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["first_name"] == "Оновлена"
    assert body["phone"] == "+380509998877"


def test_admin_cannot_block_himself(client: TestClient, admin) -> None:
    response = client.patch(
        f"/api/v1/users/{admin.id}/status",
        json={"is_active": False},
        headers=auth_headers(client, admin.email),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "BUSINESS_RULE_VIOLATION"


def test_admin_blocks_and_activates_user(client: TestClient, admin, customer) -> None:
    headers = auth_headers(client, admin.email)

    blocked = client.patch(
        f"/api/v1/users/{customer.id}/status", json={"is_active": False}, headers=headers
    )
    assert blocked.status_code == 200
    assert blocked.json()["is_active"] is False

    activated = client.patch(
        f"/api/v1/users/{customer.id}/status", json={"is_active": True}, headers=headers
    )
    assert activated.status_code == 200
    assert activated.json()["is_active"] is True


def test_customer_can_read_own_profile_but_not_others(
    client: TestClient, customer, other_customer
) -> None:
    headers = auth_headers(client, customer.email)

    own = client.get(f"/api/v1/users/{customer.id}", headers=headers)
    assert own.status_code == 200

    foreign = client.get(f"/api/v1/users/{other_customer.id}", headers=headers)
    assert foreign.status_code == 403


def test_customer_updates_own_profile(client: TestClient, customer) -> None:
    response = client.patch(
        "/api/v1/users/me",
        json={"first_name": "Оновлене", "phone": "+380501234567"},
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Оновлене"


def test_search_and_filters_work_on_server(
    client: TestClient, db_session: Session, admin
) -> None:
    create_user(
        db_session,
        email="ivan.search@test.ua",
        role=UserRole.CUSTOMER,
        first_name="Іван",
        last_name="Пошуковий",
        phone="+380671112200",
    )
    create_user(
        db_session,
        email="petro.search@test.ua",
        role=UserRole.COURIER,
        first_name="Петро",
        last_name="Кур'єрський",
        phone="+380671112201",
        is_active=False,
    )
    headers = auth_headers(client, admin.email)

    by_name = client.get("/api/v1/users", params={"search": "Іван"}, headers=headers)
    assert by_name.json()["meta"]["total"] == 1

    by_phone = client.get("/api/v1/users", params={"search": "1112201"}, headers=headers)
    assert by_phone.json()["meta"]["total"] == 1

    by_role = client.get("/api/v1/users", params={"role": "COURIER"}, headers=headers)
    assert by_role.json()["meta"]["total"] == 1

    inactive = client.get("/api/v1/users", params={"is_active": "false"}, headers=headers)
    assert inactive.json()["meta"]["total"] == 1


def test_pagination_and_sorting(client: TestClient, db_session: Session, admin) -> None:
    for index in range(5):
        create_user(
            db_session,
            email=f"paged{index}@test.ua",
            role=UserRole.CUSTOMER,
            first_name=f"Клієнт{index}",
            last_name="Сторінковий",
            phone=f"+38067111230{index}",
        )
    headers = auth_headers(client, admin.email)

    first_page = client.get(
        "/api/v1/users",
        params={"page": 1, "page_size": 2, "sort_by": "email", "sort_order": "asc"},
        headers=headers,
    ).json()
    assert len(first_page["items"]) == 2
    assert first_page["meta"]["total"] == 6
    assert first_page["meta"]["total_pages"] == 3

    second_page = client.get(
        "/api/v1/users",
        params={"page": 2, "page_size": 2, "sort_by": "email", "sort_order": "asc"},
        headers=headers,
    ).json()
    first_emails = {item["email"] for item in first_page["items"]}
    second_emails = {item["email"] for item in second_page["items"]}
    assert first_emails.isdisjoint(second_emails)


def test_staff_can_fetch_customer_options(client: TestClient, dispatcher, customer) -> None:
    response = client.get("/api/v1/users/customers", headers=auth_headers(client, dispatcher.email))
    assert response.status_code == 200
    emails = [item["email"] for item in response.json()]
    assert customer.email in emails


def test_customer_cannot_fetch_customer_options(client: TestClient, customer) -> None:
    response = client.get("/api/v1/users/customers", headers=auth_headers(client, customer.email))
    assert response.status_code == 403
