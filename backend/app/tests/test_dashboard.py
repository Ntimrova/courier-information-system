"""Тести зведення dashboard."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.conftest import auth_headers, order_payload


def _create_order(client: TestClient, email: str) -> dict:
    response = client.post(
        "/api/v1/orders", json=order_payload(), headers=auth_headers(client, email)
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_dashboard_for_dispatcher_counts_all_orders(
    client: TestClient, dispatcher, customer, other_customer
) -> None:
    first = _create_order(client, customer.email)
    _create_order(client, other_customer.email)
    third = _create_order(client, customer.email)

    headers = auth_headers(client, dispatcher.email)
    client.post(
        f"/api/v1/orders/{first['id']}/status", json={"status": "CONFIRMED"}, headers=headers
    )
    client.post(
        f"/api/v1/orders/{third['id']}/status", json={"status": "CANCELLED"}, headers=headers
    )

    body = client.get("/api/v1/dashboard/summary", headers=headers).json()
    assert body["scope"] == "all"
    counters = body["counters"]
    assert counters["total"] == 3
    assert counters["created"] == 1
    assert counters["confirmed"] == 1
    assert counters["cancelled"] == 1
    assert counters["waiting_for_courier"] == 0
    assert counters["active"] == 2
    assert len(body["recent_orders"]) == 3


def test_dashboard_for_customer_counts_only_own(
    client: TestClient, customer, other_customer
) -> None:
    _create_order(client, customer.email)
    _create_order(client, other_customer.email)

    body = client.get(
        "/api/v1/dashboard/summary", headers=auth_headers(client, customer.email)
    ).json()
    assert body["scope"] == "own"
    assert body["counters"]["total"] == 1
    assert body["total_users"] is None


def test_dashboard_for_admin_includes_user_counters(
    client: TestClient, admin, customer
) -> None:
    body = client.get(
        "/api/v1/dashboard/summary", headers=auth_headers(client, admin.email)
    ).json()
    assert body["total_users"] == 2
    assert body["active_users"] == 2


def test_dashboard_recent_orders_limited_to_five(client: TestClient, customer) -> None:
    for _ in range(7):
        _create_order(client, customer.email)
    body = client.get(
        "/api/v1/dashboard/summary", headers=auth_headers(client, customer.email)
    ).json()
    assert body["counters"]["total"] == 7
    assert len(body["recent_orders"]) == 5


def test_dashboard_for_courier_is_empty_in_part_one(
    client: TestClient, courier, customer
) -> None:
    _create_order(client, customer.email)
    body = client.get(
        "/api/v1/dashboard/summary", headers=auth_headers(client, courier.email)
    ).json()
    assert body["scope"] == "none"
    assert body["counters"]["total"] == 0
    assert body["recent_orders"] == []


def test_dashboard_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/dashboard/summary").status_code == 401
