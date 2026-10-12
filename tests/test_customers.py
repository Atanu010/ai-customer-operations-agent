from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_customer_details() -> None:
    response = client.get("/api/customers/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["customer"]["id"] == 1
    assert payload["customer"]["name"] == "Ava Patel"


def test_get_customer_orders() -> None:
    response = client.get("/api/customers/1/orders")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert payload[0]["product_name"] in {"Wireless Headphones", "Smartwatch"}


def test_missing_customer_returns_404() -> None:
    response = client.get("/api/customers/999")
    assert response.status_code == 404
