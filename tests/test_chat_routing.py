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
    response = client.post(
        "/api/chat",
        json={"message": message, "user_id": 1, "history": []},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["agent_type"] == expected_agent
    assert result["response"]
    assert 0 <= result["confidence"] <= 1


def test_chat_history_preserves_agent_context():
    response = client.post(
        "/api/chat",
        json={
            "message": "Can you keep helping with that?",
            "user_id": 7,
            "history": [
                {"role": "user", "content": "I need help with a refund"},
                {
                    "role": "assistant",
                    "content": "Support here. I can help with the refund request.",
                    "agent_type": "support",
                },
            ],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["agent_type"] == "support"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard_view():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "AI Workforce Dashboard" in response.text
