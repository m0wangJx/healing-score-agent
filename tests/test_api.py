from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Healing Score Agent is running"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_message_low_risk():
    payload = {
        "user_text": "我今天有点累，但还好",
        "session_id": "test-low-001",
    }
    response = client.post("/chat/message", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["risk_level"] == "low"
    assert data["score"] == 20


def test_chat_message_medium_risk():
    payload = {
        "user_text": "我最近很难过，感觉没有希望了",
        "session_id": "test-medium-001",
    }
    response = client.post("/chat/message", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["risk_level"] == "medium"
    assert data["score"] == 60


def test_chat_message_high_risk():
    payload = {
        "user_text": "我觉得活着没意义，我不想活了",
        "session_id": "test-high-001",
    }
    response = client.post("/chat/message", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["risk_level"] == "high"
    assert data["score"] == 90