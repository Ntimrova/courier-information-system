"""Тести створення, перегляду й редагування замовлень."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.tests.conftest import auth_headers, order_payload


def create_order_as(client: TestClient, email: str, **overrides) -> dict:
    response = client.post(
        "/api/v1/orders", json=order_payload(**overrides), headers=auth_headers(client, email)
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_customer_creates_order(client: TestClient, customer) -> None:
    body = create_order_as(client, customer.email)
    assert body["status"] == "CREATED"
    assert body["customer_id"] == customer.id
    assert body["tracking_number"].startswith(f"LDC-{date.today().year}-")
    assert len(body["tracking_number"]) == len(f"LDC-{date.today().year}-000001")


def test_tracking_numbers_are_sequential_and_unique(client: TestClient, customer) -> None:
    first = create_order_as(client, customer.email)
    second = create_order_as(client, customer.email)
    assert first["tracking_number"] != second["tracking_number"]
    assert first["tracking_number"].endswith("000001")
    assert second["tracking_number"].endswith("000002")


def test_customer_sees_only_own_orders(client: TestClient, customer, other_customer) -> None:
    create_order_as(client, customer.email)
    create_order_as(client, other_customer.email)

    response = client.get("/api/v1/orders", headers=auth_headers(client, customer.email))
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == 1
    assert body["items"][0]["customer_id"] == customer.id


def test_customer_cannot_read_foreign_order(
    client: TestClient, customer, other_customer
) -> None:
    foreign = create_order_as(client, other_customer.email)
    response = client.get(
        f"/api/v1/orders/{foreign['id']}", headers=auth_headers(client, customer.email)
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_customer_cannot_read_foreign_order_history(
    client: TestClient, customer, other_customer
) -> None:
    foreign = create_order_as(client, other_customer.email)
    response = client.get(
        f"/api/v1/orders/{foreign['id']}/history", headers=auth_headers(client, customer.email)
    )
    assert response.status_code == 403


def test_dispatcher_sees_all_orders(
    client: TestClient, dispatcher, customer, other_customer
) -> None:
    create_order_as(client, customer.email)
    create_order_as(client, other_customer.email)

    response = client.get("/api/v1/orders", headers=auth_headers(client, dispatcher.email))
    assert response.json()["meta"]["total"] == 2


def test_courier_has_no_orders_in_part_one(client: TestClient, courier, customer) -> None:
    order = create_order_as(client, customer.email)
    headers = auth_headers(client, courier.email)

    listing = client.get("/api/v1/orders", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["meta"]["total"] == 0

    detail = client.get(f"/api/v1/orders/{order['id']}", headers=headers)
    assert detail.status_code == 403


def test_dispatcher_creates_order_for_customer(client: TestClient, dispatcher, customer) -> None:
    response = client.post(
        "/api/v1/orders",
        json=order_payload(customer_id=customer.id),
        headers=auth_headers(client, dispatcher.email),
    )
    assert response.status_code == 201, response.text
    assert response.json()["customer_id"] == customer.id


def test_dispatcher_must_specify_customer(client: TestClient, dispatcher) -> None:
    response = client.post(
        "/api/v1/orders", json=order_payload(), headers=auth_headers(client, dispatcher.email)
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_customer_id_from_customer_is_ignored(
    client: TestClient, customer, other_customer
) -> None:
    """Клієнт не може оформити замовлення на чуже ім'я."""
    response = client.post(
        "/api/v1/orders",
        json=order_payload(customer_id=other_customer.id),
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 201
    assert response.json()["customer_id"] == customer.id


def test_order_validation_weight_must_be_positive(client: TestClient, customer) -> None:
    response = client.post(
        "/api/v1/orders",
        json=order_payload(package_weight="0"),
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_order_validation_date_cannot_be_in_past(client: TestClient, customer) -> None:
    response = client.post(
        "/api/v1/orders",
        json=order_payload(desired_delivery_date=(date.today() - timedelta(days=1)).isoformat()),
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 422


def test_order_validation_addresses_must_differ(client: TestClient, customer) -> None:
    same_address = "м. Київ, вул. Хрещатик, 22"
    response = client.post(
        "/api/v1/orders",
        json=order_payload(pickup_address=same_address, delivery_address=same_address),
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 422


def test_order_validation_phone_format(client: TestClient, customer) -> None:
    response = client.post(
        "/api/v1/orders",
        json=order_payload(recipient_phone="abc"),
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 422


def test_order_validation_required_fields(client: TestClient, customer) -> None:
    payload = order_payload()
    del payload["recipient_name"]
    response = client.post(
        "/api/v1/orders", json=payload, headers=auth_headers(client, customer.email)
    )
    assert response.status_code == 422


def test_customer_updates_own_order(client: TestClient, customer) -> None:
    order = create_order_as(client, customer.email)
    response = client.patch(
        f"/api/v1/orders/{order['id']}",
        json={"comment": "Новий коментар", "package_weight": "2.250"},
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["comment"] == "Новий коментар"
    assert body["package_weight"] == "2.250"


def test_customer_cannot_update_foreign_order(
    client: TestClient, customer, other_customer
) -> None:
    foreign = create_order_as(client, other_customer.email)
    response = client.patch(
        f"/api/v1/orders/{foreign['id']}",
        json={"comment": "Чуже замовлення"},
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 403


def test_update_rejects_equal_addresses(client: TestClient, customer) -> None:
    order = create_order_as(client, customer.email)
    response = client.patch(
        f"/api/v1/orders/{order['id']}",
        json={"delivery_address": order["pickup_address"]},
        headers=auth_headers(client, customer.email),
    )
    assert response.status_code == 422


def test_order_not_found(client: TestClient, customer) -> None:
    response = client.get("/api/v1/orders/999999", headers=auth_headers(client, customer.email))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ORDER_NOT_FOUND"


def test_orders_search_filter_and_pagination(
    client: TestClient, dispatcher, customer, other_customer
) -> None:
    first = create_order_as(client, customer.email, recipient_phone="+380931112233")
    create_order_as(
        client,
        other_customer.email,
        delivery_type="EXPRESS",
        recipient_phone="+380509998877",
        desired_delivery_date=(date.today() + timedelta(days=10)).isoformat(),
    )
    headers = auth_headers(client, dispatcher.email)

    by_tracking = client.get(
        "/api/v1/orders", params={"search": first["tracking_number"]}, headers=headers
    )
    assert by_tracking.json()["meta"]["total"] == 1

    by_phone = client.get("/api/v1/orders", params={"search": "9998877"}, headers=headers)
    assert by_phone.json()["meta"]["total"] == 1

    by_type = client.get("/api/v1/orders", params={"delivery_type": "EXPRESS"}, headers=headers)
    assert by_type.json()["meta"]["total"] == 1

    by_date = client.get(
        "/api/v1/orders",
        params={"date_from": (date.today() + timedelta(days=5)).isoformat()},
        headers=headers,
    )
    assert by_date.json()["meta"]["total"] == 1

    paged = client.get("/api/v1/orders", params={"page": 1, "page_size": 1}, headers=headers)
    body = paged.json()
    assert len(body["items"]) == 1
    assert body["meta"]["total"] == 2
    assert body["meta"]["total_pages"] == 2


def test_customer_search_stays_inside_own_orders(
    client: TestClient, customer, other_customer
) -> None:
    foreign = create_order_as(client, other_customer.email)
    response = client.get(
        "/api/v1/orders",
        params={"search": foreign["tracking_number"], "customer_id": other_customer.id},
        headers=auth_headers(client, customer.email),
    )
    assert response.json()["meta"]["total"] == 0
