from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_order_by_id() -> None:
    response = client.get("/api/orders/1001")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1001
    assert payload["status"] == "in_transit"


def test_invalid_order_id() -> None:
    response = client.get("/api/orders/-1")
    assert response.status_code == 422


def test_missing_order_returns_404() -> None:
    response = client.get("/api/orders/99999")
    assert response.status_code == 404
