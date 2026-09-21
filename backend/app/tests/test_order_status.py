"""Тести переходів статусів, скасування та історії."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.enums import OrderStatus
from app.services import status_rules
from app.tests.conftest import auth_headers, order_payload


def _create_order(client: TestClient, email: str) -> dict:
    response = client.post(
        "/api/v1/orders", json=order_payload(), headers=auth_headers(client, email)
    )
    assert response.status_code == 201, response.text
    return response.json()


def _set_status(client: TestClient, email: str, order_id: int, status: str, comment=None):
    payload: dict = {"status": status}
    if comment is not None:
        payload["comment"] = comment
    return client.post(
        f"/api/v1/orders/{order_id}/status", json=payload, headers=auth_headers(client, email)
    )


# ---------------------------------------------------------------------------
# Правила переходів (чиста функція, без HTTP)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (OrderStatus.CREATED, OrderStatus.CONFIRMED),
        (OrderStatus.CREATED, OrderStatus.CANCELLED),
        (OrderStatus.CONFIRMED, OrderStatus.WAITING_FOR_COURIER),
        (OrderStatus.CONFIRMED, OrderStatus.CANCELLED),
        (OrderStatus.WAITING_FOR_COURIER, OrderStatus.CANCELLED),
    ],
)
def test_allowed_transitions(current: OrderStatus, target: OrderStatus) -> None:
    assert status_rules.is_transition_allowed(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (OrderStatus.CREATED, OrderStatus.WAITING_FOR_COURIER),
        (OrderStatus.CONFIRMED, OrderStatus.CREATED),
        (OrderStatus.WAITING_FOR_COURIER, OrderStatus.CONFIRMED),
        (OrderStatus.CANCELLED, OrderStatus.CONFIRMED),
        (OrderStatus.CREATED, OrderStatus.DELIVERED),
    ],
)
def test_forbidden_transitions(current: OrderStatus, target: OrderStatus) -> None:
    assert not status_rules.is_transition_allowed(current, target)


# ---------------------------------------------------------------------------
# Зміна статусу через API
# ---------------------------------------------------------------------------


def test_dispatcher_confirms_order(client: TestClient, dispatcher, customer) -> None:
    order = _create_order(client, customer.email)
    response = _set_status(client, dispatcher.email, order["id"], "CONFIRMED", "Все перевірено")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CONFIRMED"


def test_full_allowed_chain(client: TestClient, dispatcher, customer) -> None:
    order = _create_order(client, customer.email)
    assert _set_status(client, dispatcher.email, order["id"], "CONFIRMED").status_code == 200
    response = _set_status(client, dispatcher.email, order["id"], "WAITING_FOR_COURIER")
    assert response.status_code == 200
    assert response.json()["status"] == "WAITING_FOR_COURIER"


def test_invalid_transition_is_rejected(client: TestClient, dispatcher, customer) -> None:
    order = _create_order(client, customer.email)
    response = _set_status(client, dispatcher.email, order["id"], "WAITING_FOR_COURIER")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"


def test_transition_to_part_two_status_is_rejected(
    client: TestClient, dispatcher, customer
) -> None:
    """Статуси частини 2 є в enum, але поки недосяжні."""
    order = _create_order(client, customer.email)
    response = _set_status(client, dispatcher.email, order["id"], "DELIVERED")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"


def test_same_status_is_rejected(client: TestClient, dispatcher, customer) -> None:
    order = _create_order(client, customer.email)
    response = _set_status(client, dispatcher.email, order["id"], "CREATED")
    assert response.status_code == 409


def test_customer_cannot_change_status(client: TestClient, customer) -> None:
    order = _create_order(client, customer.email)
    response = _set_status(client, customer.email, order["id"], "CONFIRMED")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_cancelled_order_cannot_move_further(client: TestClient, dispatcher, customer) -> None:
    order = _create_order(client, customer.email)
    assert _set_status(client, dispatcher.email, order["id"], "CANCELLED").status_code == 200
    response = _set_status(client, dispatcher.email, order["id"], "CONFIRMED")
    assert response.status_code == 409


# ---------------------------------------------------------------------------
# Скасування
# ---------------------------------------------------------------------------


def test_customer_cancels_own_order(client: TestClient, customer) -> None:
    order = _create_order(client, customer.email)
    response = client.post(
        f"/api/v1/orders/{order['id']}/cancel",
        json={"comment": "Передумала"},
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "CANCELLED"
    assert body["cancelled_at"] is not None


def test_customer_cannot_cancel_foreign_order(
    client: TestClient, customer, other_customer
) -> None:
    foreign = _create_order(client, other_customer.email)
    response = client.post(
        f"/api/v1/orders/{foreign['id']}/cancel",
        json={},
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 403


def test_double_cancel_is_rejected(client: TestClient, customer) -> None:
    order = _create_order(client, customer.email)
    headers = auth_headers(client, customer.email)
    assert (
        client.post(f"/api/v1/orders/{order['id']}/cancel", json={}, headers=headers).status_code
        == 200
    )
    response = client.post(f"/api/v1/orders/{order['id']}/cancel", json={}, headers=headers)
    assert response.status_code == 409


def test_cancelled_order_cannot_be_edited(client: TestClient, customer) -> None:
    order = _create_order(client, customer.email)
    headers = auth_headers(client, customer.email)
    client.post(f"/api/v1/orders/{order['id']}/cancel", json={}, headers=headers)

    response = client.patch(
        f"/api/v1/orders/{order['id']}", json={"comment": "Пізня правка"}, headers=headers
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "BUSINESS_RULE_VIOLATION"


# ---------------------------------------------------------------------------
# Історія статусів
# ---------------------------------------------------------------------------


def test_history_records_creation(client: TestClient, customer) -> None:
    order = _create_order(client, customer.email)
    response = client.get(
        f"/api/v1/orders/{order['id']}/history", headers=auth_headers(client, customer.email)
    )
    assert response.status_code == 200
    entries = response.json()
    assert len(entries) == 1
    assert entries[0]["previous_status"] is None
    assert entries[0]["new_status"] == "CREATED"
    assert entries[0]["changed_by_user_id"] == customer.id


def test_history_records_every_change(client: TestClient, dispatcher, customer) -> None:
    order = _create_order(client, customer.email)
    _set_status(client, dispatcher.email, order["id"], "CONFIRMED", "Підтверджено")
    _set_status(client, dispatcher.email, order["id"], "WAITING_FOR_COURIER", "Чекає кур'єра")
    client.post(
        f"/api/v1/orders/{order['id']}/cancel",
        json={"comment": "Скасовано диспетчером"},
        headers=auth_headers(client, dispatcher.email),
    )

    entries = client.get(
        f"/api/v1/orders/{order['id']}/history", headers=auth_headers(client, dispatcher.email)
    ).json()

    assert [entry["new_status"] for entry in entries] == [
        "CREATED",
        "CONFIRMED",
        "WAITING_FOR_COURIER",
        "CANCELLED",
    ]
    assert [entry["previous_status"] for entry in entries] == [
        None,
        "CREATED",
        "CONFIRMED",
        "WAITING_FOR_COURIER",
    ]
    assert entries[1]["comment"] == "Підтверджено"
    assert entries[1]["changed_by"]["id"] == dispatcher.id


def test_failed_transition_does_not_write_history(
    client: TestClient, dispatcher, customer
) -> None:
    order = _create_order(client, customer.email)
    _set_status(client, dispatcher.email, order["id"], "DELIVERED")

    entries = client.get(
        f"/api/v1/orders/{order['id']}/history", headers=auth_headers(client, dispatcher.email)
    ).json()
    assert len(entries) == 1
