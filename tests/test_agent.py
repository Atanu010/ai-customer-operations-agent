import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("Where is my order 1001?", "ORDER_STATUS"),
        ("What did I buy in order 1002?", "ORDER_DETAILS"),
        ("Can I return an item after delivery?", "RETURN_POLICY"),
        ("My package is late.", "DELIVERY_DELAY"),
        ("I need general help.", "GENERAL_SUPPORT"),
    ],
)
def test_agent_classifies_intent(message: str, expected_intent: str) -> None:
    response = client.post("/api/agent/query", json={"message": message})
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == expected_intent


def test_agent_unknown_request() -> None:
    response = client.post("/api/agent/query", json={"message": "I have a question about a random alien device."})
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] in {"UNKNOWN", "GENERAL_SUPPORT"}
