from fastapi.testclient import TestClient

from agentshield.app import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_frontend_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "AgentShield" in response.text
    assert "Run assessment" in response.text


def test_scenarios_are_synthetic():
    response = client.get("/scenarios")
    assert response.status_code == 200
    assert all("synthetic" in item["prompt"].lower() or item["id"] == "benign-read" or "fixture" in item["prompt"].lower()
               for item in response.json())


def test_assess_flags_disallowed_tool():
    response = client.post("/assess", json={"actions": [{"tool": "shell", "source": "tool"}]})
    assert response.status_code == 200
    assert response.json()["passed"] is False
