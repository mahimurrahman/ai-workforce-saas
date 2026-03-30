import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize("message,expected_agent", [
    ("I need support with a refund", "support"),
    ("What are your pricing plans?", "sales"),
    ("How do I update my workflow process?", "ops"),
])
def test_chat_routing(message, expected_agent):
    response = client.post("/api/chat", json={"message": message, "user_id": 1, "context": {}})
    assert response.status_code == 200
    result = response.json()
    assert result["agent_type"] == expected_agent


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard_view():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "AI Workforce Dashboard" in response.text
